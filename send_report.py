import csv
import os
import smtplib
from io import StringIO
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_monthly_report():
    today = datetime.now()
    response = supabase.table("kind_dict").select("*").execute()
    rows = response.data

    if not rows:
        print(f"[{today}] 전송할 데이터가 없습니다.")
        return

    output = StringIO()
    csv_writer = csv.DictWriter(output, fieldnames=["id", "word_to_search", "input", "searched_at", "selected_language", "none_in_dict"])
    csv_writer.writeheader()
    csv_writer.writerows(rows)
    output.seek(0)

    msg = MIMEMultipart()
    msg["From"] = "sfc27@naver.com"
    msg["To"] = "sfc27@naver.com"
    msg["Subject"] = "월간데이터_친절한 한국어 검색 사전"
    msg.attach(MIMEText("첨부된 파일을 확인하세요.", "plain"))

    csv_data = output.getvalue().encode('utf-8-sig')
    part = MIMEBase("application", "octet-stream")
    part.set_payload(csv_data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename="kind_dict_report.csv")
    msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.naver.com", 465) as smtp:
            smtp.login("sfc27", EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"[{today}] 이메일이 성공적으로 전송되었습니다.")
    except Exception as e:
        print(f"[{today}] 이메일 전송 중 오류 발생: {e}")

    try:
        supabase.table("kind_dict").delete().neq("id", 0).execute()
        print(f"[{today}] 데이터가 삭제되었습니다.")
    except Exception as e:
        print(f"[{today}] Supabase 데이터 삭제 중 오류 발생: {e}")

if __name__ == "__main__":
    send_monthly_report()
