import streamlit as st
from google import genai

st.set_page_config(page_title="محرر البيان الذكي", page_icon="🖋️", layout="centered")

st.title("🖋️ محرر البيان الذكي")
st.caption("إعادة صياغة النصوص بين بلاغة الجاحظ وتأثير المحتوى العصري")

with st.sidebar:
    st.header("الإعدادات")
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")
    st.markdown("[احصل على مفتاح مجاني من Google AI Studio](https://aistudio.google.com/)")

user_text = st.text_area("أدخل النص الذي تريد تحسينه وصياغته:", height=150, placeholder="اكتب أو الصق نصك هنا...")

SYSTEM_PROMPT = """أنت "محرر البيان الذكي"، مساعد ذكي متخصص في البلاغة العربية ونقد الأدب بأسلوب الجاحظ (صاحب البيان والتبيين)، وخبير في صياغة المحتوى الرقمي العصري (Copywriting & Micro-content).

مهمتك:
استلام النصوص المدخلة من المستخدم، وتطهيرها من العيوب البلاغية واللغوية، ثم إعادة صياغتها لتكون أكثر تأثيراً وقوة وجاذبية للجمهور المعاصر دون الإخلال بسلامة اللغة وجزالتها.

ضوابط ومعايير الصياغة (مستوحاة من البيان والتبيين):
1. مطابقة مقتضى الحال: إدراك طبيعة الجمهور والاستغناء عن التكلف والغريب من الألفاظ.
2. نفي الفضول وحذف الحشو: إزالة الكلمات الزائدة والترادف غير النافع، وتطبيق مبدأ "البلاغة الإيجاز".
3. نصاعة اللفظ وحسن السباكة: اختيار المفردات ذات الإيقاع الصوتي المتناسق، وتجنب تنافر الحروف والتعقيد اللفظي.
4. الخاطف البصري والصوتي (The Hook): جعل مطلع النص قوياً ومباشراً يجذب انتباه القارئ أو المستمع من اللحظة الأولى.

قواعد الإخراج الإلزامية:
عند استلام أي نص، قم بتحليله وإعادة صياغته وقدم النتيجة حصراً وفق الهيكلية التالية:

---
### 1. النسخة الخطابية القيادية (Official & Public Speaking)
[نص صلب، جزل، ومناسب للإلقاء والعروض التقديمية]

### 2. نسخة المحتوى الرقمي السريع (Social Media & Copywriting)
[نص قصير، مشوق، مقسم إلى أسطر قصيرة يحتوي على Hook خاطف]

### 3. التقرير البلاغي الخاطف (Al-Jahiz Critique)
- **سبب التعديل:** [سطر واحد يوضح أهم خطأ أو حشو تم التخلص منه]
- **الدرة البلاغية:** [سطر واحد يشرح الشاهد أو القاعدة البلاغية]
---"""

def generate_with_fallback(client, prompt_text):
    # قائمة أسماء النماذج المتاحة بالتسلسل
    model_candidates = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    # 1. التجربة الأولى: اختيار أول نموذج يعمل من القائمة مباشرة
    for m in model_candidates:
        try:
            res = client.models.generate_content(model=m, contents=prompt_text)
            if res and res.text:
                return res.text
        except Exception:
            continue
            
    # 2. التجربة الثانية: البحث التلقائي عن أي نموذج يعمل في مفتاح المستخدم
    try:
        available_models = client.models.list()
        for model_info in available_models:
            model_id = getattr(model_info, 'name', '') or str(model_info)
            if "gemini" in model_id.lower():
                try:
                    res = client.models.generate_content(model=model_id, contents=prompt_text)
                    if res and res.text:
                        return res.text
                except Exception:
                    continue
    except Exception:
        pass

    raise Exception("لم نتمكن من الوصول لنماذج Gemini المتاحة، يرجى التأكد من صحة المفتاح المُدخل.")

if st.button("صياغة البيان ✨", use_container_width=True):
    if not api_key:
        st.error("يرجى إدخل مفتاح Gemini API في الشريط الجانبي للاستمرار.")
    elif not user_text.strip():
        st.warning("يرجى إدخال نص لصياغته.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("جاري تحليل النص وإعادة صياغته بأسلوب البيان..."):
                full_prompt = f"{SYSTEM_PROMPT}\n\nالنص المدخل من المستخدم:\n{user_text}"
                output_text = generate_with_fallback(client, full_prompt)
                st.markdown("---")
                st.markdown(output_text)
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
