import copy
import math
import re
from pathlib import Path

import cv2
import easyocr
import numpy as np
import torch
import torchvision
from django.conf import settings
from pdf2image import convert_from_path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from torchvision.models.detection import MaskRCNN_ResNet50_FPN_Weights
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision.transforms import transforms
from tqdm import tqdm
from transformers import AutoModelForSeq2SeqLM
from transformers import AutoTokenizer

from .text_wrap_vnm import fw_fill_vi

CATEGORIES2LABELS = {
    0: "bg",
    1: "text",
    2: "title",
    3: "list",
    4: "table",
    5: "figure",
}

MODEL_PATH = Path(settings.STATIC_ROOT) / "model_196000.pth"


def get_instance_segmentation_model(num_classes):
    """
    This function returns a Mask R-CNN model with a ResNet-50-FPN backbone.
    The model is pretrained on the PubLayNet dataset.
    -----
    Input:
        num_classes: number of classes
    Output:
        model: Mask R-CNN model with a ResNet-50-FPN backbone
    """
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(
        weights=MaskRCNN_ResNet50_FPN_Weights.DEFAULT,
    )
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256

    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer,
        num_classes,
    )
    return model


class TranslationLayoutRecovery:
    """TranslationLayoutRecovery class.

    Attributes from _load_init()
    ----------
    font: ImageFont
        Font for drawing text on the image
    ocr_model: EasyOCR
        OCR model for detecting text in the text blocks
    translate_model:
        Translation model for translating text
    translate_tokenizer:
        Tokenizer for decoding the output of the translation model
    """

    DPI = 300
    FONT_SIZE_VIETNAMESE = 34
    MAGIC_NUMBER = 15
    THRESHOLD = 0.7

    def __init__(self):
        self._load_init()

    def translate_text(self, en_text: str) -> str:
        input_ids = self.tokenizer(en_text, return_tensors="pt").input_ids
        output_ids = self.model.generate(
            input_ids,
            decoder_start_token_id=self.tokenizer.lang_code_to_id["vi_VN"],
            num_return_sequences=1,
            num_beams=5,
            early_stopping=True,
        )
        vi_text = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        return " ".join(vi_text)

    def _repeated_substring(self, s: str):
        n = len(s)
        for i in range(10, n // 2 + 1):
            pattern = s[:i]
            matches = list(re.finditer(rf"\b{re.escape(pattern)}\b", s))
            if len(matches) >= self.MAGIC_NUMBER:
                return True
        for i in range(n // 2 + 11, n):
            pattern = s[n // 2 + 1 : i]
            matches = list(re.finditer(rf"\b{re.escape(pattern)}\b", s))
            if len(matches) >= self.MAGIC_NUMBER:
                return True
        return False

    def translate_pdf(
        self,
        input_path: Path | bytes,
        output_path: Path,
    ) -> None:
        """Backend function for translating PDF files.

        Translation is performed in the following steps:
            1. Convert the PDF file to images
            2. Detect text blocks in the images
            3. For each text block, detect text and translate it
            4. Draw the translated text on the image
            5. Save the image as a PDF file
            6. Merge all PDF files into one PDF file

        At 3, this function does not translate the text after
        the references section. Instead, saves the image as it is.

        Parameters
        ----------
        input_path: Union[Path, bytes]
            Path to the input PDF file or bytes of the input PDF file
        output_path: Path
            Path to the output directory
        """
        pdf_images = convert_from_path(input_path, dpi=self.DPI)
        reached_references = False

        # Batch
        idx = 0
        batch_size = 8
        pil_images = []
        for _ in tqdm(range(math.ceil(len(pdf_images) / batch_size))):
            image_list = pdf_images[idx : idx + batch_size]
            if not reached_references:
                image_list, reached_references = self._translate_multiple_pages(
                    image_list=image_list,
                    reached_references=reached_references,
                )

            for [translated_image, _] in image_list:
                pil_image = Image.fromarray(translated_image)
                pil_image = pil_image.convert("RGB")
                pil_images.append(pil_image)

            idx += batch_size

        pil_images[0].save(
            output_path / input_path.name,
            "PDF",
            resolution=100.00,
            save_all=True,
            append_images=pil_images[1:],
        )

    def _load_init(self):
        """Backend function for loading models.

        Called in the constructor.
        Load the layout model, OCR model, translation model and font.
        """
        self.font_vi = ImageFont.truetype(
            Path(settings.STATIC_ROOT) / "AlegreyaSans-Regular.otf",
            size=self.FONT_SIZE_VIETNAMESE,
        )

        # Detection model: PubLayNet
        self.num_classes = len(CATEGORIES2LABELS.keys())
        self.pub_model = get_instance_segmentation_model(self.num_classes)

        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        self.pub_model.load_state_dict(checkpoint["model"])
        self.pub_model.eval()

        # Recognition model: PaddleOCR
        self.ocr_model = easyocr.Reader(["en"], model_storage_directory=settings.STATIC_ROOT + "/easyocr")

        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.ToTensor(),
            ],
        )

        self.tokenizer = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi-v2", src_lang="en_XX")
        model_path = Path(settings.STATIC_ROOT) / "model"
        if model_path.exists():
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        else:
            self.model = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi-v2")
        self.model.save_pretrained(model_path)

    def _crop_img(self, box, ori_img):
        new_box_0 = int(box[0] / self.rat) - 20
        new_box_1 = int(box[1] / self.rat) - 10
        new_box_2 = int(box[2] / self.rat) + 20
        new_box_3 = int(box[3] / self.rat) + 10
        temp_img = ori_img[new_box_1:new_box_3, new_box_0:new_box_2]
        box = [new_box_0, new_box_1, new_box_2, new_box_3]
        return temp_img, box

    def _ocr_module(self, list_boxes, list_labels_idx, ori_img):
        original_image = copy.deepcopy(ori_img)
        list_labels = list(map(lambda y: CATEGORIES2LABELS[y.item()], list_labels_idx))
        list_masks = list(map(lambda x: x == "text", list_labels))
        list_boxes_filtered = list_boxes[list_masks]
        list_images_filtered = [original_image] * len(list_boxes_filtered)

        results = list(map(self._crop_img, list_boxes_filtered, list_images_filtered))

        if len(results) > 0:
            list_temp_images, list_new_boxes = (
                [row[0] for row in results],
                [row[1] for row in results],
            )

            list_ocr_results = list(
                map(
                    lambda x: np.array(x, dtype=object)[:, 1] if len(x) > 0 else None,
                    list(map(lambda x: self.ocr_model.readtext(x), list_temp_images)),
                ),
            )

            for ocr_results, box in zip(list_ocr_results, list_new_boxes, strict=False):
                if ocr_results is not None:
                    ocr_text = " ".join(ocr_results)
                    if len(ocr_text) > 1:
                        text = re.sub(r"\n|\t|\[|\]|\/|\|", " ", ocr_text)
                        translated_text = self.translate_text(text)
                        translated_text = re.sub(
                            r"\n|\t|\[|\]|\/|\|",
                            " ",
                            translated_text,
                        )

                        if self._repeated_substring(translated_text):
                            processed_text = fw_fill_vi(
                                text,
                                width=int(
                                    (box[2] - box[0]) / (self.FONT_SIZE_VIETNAMESE / 2),
                                )
                                + 1,
                            )
                        else:
                            processed_text = fw_fill_vi(
                                translated_text,
                                width=int(
                                    (box[2] - box[0]) / (self.FONT_SIZE_VIETNAMESE / 2),
                                )
                                + 1,
                            )

                        new_block = Image.new(
                            "RGB",
                            (
                                box[2] - box[0],
                                box[3] - box[1],
                            ),
                            color=(255, 255, 255),
                        )
                        draw = ImageDraw.Draw(new_block)
                        draw.text(
                            (0, 0),
                            text=processed_text,
                            font=self.font_vi,
                            fill=(0, 0, 0),
                        )

                        new_block = np.array(new_block)
                        original_image[
                            int(box[1]) : int(box[3]),
                            int(box[0]) : int(box[2]),
                        ] = new_block
                else:
                    continue

        reached_references = False

        # Check title "Reference" or "References", if so then stop
        list_title_masks = list(map(lambda x: x == "title", list_labels))
        list_boxes_filtered = list_boxes[list_title_masks]
        list_images_filtered = [original_image] * len(list_boxes_filtered)

        results = list(map(self._crop_img, list_boxes_filtered, list_images_filtered))
        if len(results) > 0:
            list_temp_images = [row[0] for row in results]
            list_title_ocr_results = list(
                map(
                    lambda x: np.array(x, dtype=object)[:, 1] if len(x) > 0 else None,
                    list(map(lambda x: self.ocr_model.readtext(x), list_temp_images)),
                ),
            )
            if len(list_title_ocr_results) > 0:
                for result, box in zip(list_title_ocr_results, list_boxes_filtered, strict=False):
                    if result is not None:
                        if result[0].lower() in ["references", "reference"]:
                            reached_references = True
                        elif result[0].lower() == "abstract":
                            # Use the original Title and Authors, skip translating them
                            new_box_1 = int(box[1] / self.rat)
                            original_image[
                                0 : int(new_box_1),
                                0 : int(original_image.shape[1]),
                            ] = ori_img[
                                0 : int(new_box_1),
                                0 : int(ori_img.shape[1]),
                            ]

        return original_image, reached_references

    def _preprocess_image(self, image):
        ori_img = np.array(image)
        img = ori_img[:, :, ::-1].copy()

        # Get the ratio to resize
        self.rat = 1000 / img.shape[0]

        img = cv2.resize(img, None, fx=self.rat, fy=self.rat)
        img = self.transform(img).cuda()

        return [img, ori_img]

    def _translate_multiple_pages(
        self,
        image_list: list[Image.Image],
        *,
        reached_references: bool,
    ) -> tuple[np.ndarray, np.ndarray, bool]:
        """Translate one page of the PDF file.

        There are some heuristics to clean-up the results of translation:
            1. Remove newlines, tabs, brackets, slashes, and pipes
            2. Reject the result if there are few Japanese characters
            3. Skip the translation if the text block has only one line

        Parameters
        ----------
        image_list: List[Image.Image]
            Image of the page
        reached_references: bool
            Whether the references section has been reached.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, bool]
            Translated image, original image,
            and whether the references section has been reached.
        """
        results = list(map(self._preprocess_image, image_list))
        new_list_images, list_original_images = (
            [row[0] for row in results],
            [row[1] for row in results],
        )
        with torch.no_grad():
            predictions = self.pub_model(new_list_images)

        list_masks = list(map(lambda x: x["scores"] >= self.THRESHOLD, predictions))
        new_list_boxes = list(
            map(lambda x, y: x["boxes"][y, :], predictions, list_masks),
        )
        new_list_labels = list(
            map(lambda x, y: x["labels"][y], predictions, list_masks),
        )

        list_returned_images = []
        reached_references = False
        for one_image_boxes, one_image_labels, original_image in zip(
            new_list_boxes,
            new_list_labels,
            list_original_images,
            strict=False,
        ):
            one_translated_image, reached_references = self._ocr_module(
                one_image_boxes,
                one_image_labels,
                original_image,
            )
            list_returned_images.append([one_translated_image, original_image])
            if reached_references:
                break

        return list_returned_images, reached_references
