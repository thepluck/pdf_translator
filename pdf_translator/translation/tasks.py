from celery import shared_task

from .apps import TranslationConfig


@shared_task
def translate_text(en_text: str) -> str:
    tokenizer = TranslationConfig.tokenizer
    model = TranslationConfig.model
    input_ids = tokenizer(en_text, return_tensors="pt").input_ids
    output_ids = model.generate(
        input_ids,
        decoder_start_token_id=tokenizer.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True,
    )
    vi_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return " ".join(vi_text)
