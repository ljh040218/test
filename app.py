from flask import Flask, request, jsonify, send_from_directory
import os
import openai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai_api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# 업로드 폴더 경로
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
@app.route('/speech.html')
def serve_html():
    return send_from_directory('.', 'speech.html')


@app.route("/upload", methods=["POST"])
def upload_audio():
    # 업로드된 오디오 파일과 STT 텍스트 받기
    audio = request.files.get("audio")
    transcript = request.form.get("transcript", "")

    # 원래 발음(raw transcript)를 그대로 유지
    raw_transcript = transcript

    if audio is None:
        return jsonify({"error": "No audio file provided"}), 400

    # 파일 저장
    filename = audio.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    audio.save(save_path)
    print(f"오디오 저장 완료: {save_path}")

    print(f"📝 사용자 STT 텍스트: {transcript}")

    # GPT 호출해서 정답 문장 생성 (원본 발음 그대로 전달)
    answer = generate_correct_sentence(raw_transcript)

    # 결과 반환 - 원본 발음과 교정된 문장 모두 반환
    return jsonify({
        "raw_transcript": raw_transcript,  # 원본 발음 그대로
        "answer": answer                   # 교정된 문장
    })


def generate_correct_sentence(user_text: str) -> str:
    """
    OpenAI GPT 모델을 사용해
    사용자 발화문장을 자연스럽고 올바른 한국어 문장으로 교정함
    """
    prompt = (
        f"사용자의 실제 발음: \"{user_text}\"\n"
        "이 발음을 올바른 한국어 문장으로 교정해주세요. 예를 들어 '거기마 먹고 시따'는 '고구마 먹고 싶다'로 교정해야 합니다.\n"
        "발음이 정확하지 않을 수 있으므로, 사용자가 의도했을 가능성이 높은 문장들로 교정한 문장 세 개를 주세요."
    )

    try:
        # 최신 OpenAI API 사용 방식으로 변경
        client = openai.OpenAI(api_key=openai_api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 한국어 발음 교정을 돕는 교사야. 사용자의 부정확한 발음을 올바른 한국어 문장으로 교정해줘."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=100,
            temperature=0.3,
        )
        corrected_sentence = response.choices[0].message.content.strip()
        print(f"GPT 교정 결과: {corrected_sentence}")
        return corrected_sentence
    except Exception as e:
        print(f"GPT 호출 에러: {e}")
        return "죄송합니다. 문장 교정에 실패했습니다."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
