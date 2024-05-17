from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


model_name = "VietAI/envit5-translation"
tokenizer = AutoTokenizer.from_pretrained(model_name,use_fast = True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def translate_vietai(inputs):
    outputs = model.generate(tokenizer(inputs, return_tensors="pt", padding=True).input_ids, max_length=512)
    text = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return text[0].replace('vi','')

# ['en: VietAI is a non-profit organization with the mission of nurturing artificial intelligence talents and building an international - class community of artificial intelligence experts in Vietnam.',
#  'en: According to the latest LinkedIn report on the 2020 list of attractive and promising jobs, AI - related job titles such as AI Specialist, ML Engineer and ML Engineer all rank high.',
#  'vi: Nhóm chúng tôi khao khát tạo ra những khám phá có ảnh hưởng đến mọi người, và cốt lõi trong cách tiếp cận của chúng tôi là chia sẻ nghiên cứu và công cụ để thúc đẩy sự tiến bộ trong lĩnh vực này.',
#  'vi: Chúng ta đang trên hành trình tiến bộ và dân chủ hoá trí tuệ nhân tạo thông qua mã nguồn mở và khoa học mở.']
