# utils/qr_generator.py
"""Модуль генерации QR-кодов для опросов качества."""
import qrcode
from pathlib import Path
from database import get_connection

SURVEY_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?usp=sf_link"
QR_DIR = Path(__file__).parent.parent / 'data' / 'qr_codes'


def ensure_qr_dir():
    """Создать директорию для QR-кодов."""
    QR_DIR.mkdir(parents=True, exist_ok=True)


def generate_qr_code(request_id, survey_url=None):
    """Сгенерировать QR-код для опроса качества."""
    if survey_url is None:
        survey_url = SURVEY_URL
    
    ensure_qr_dir()
    full_url = f"{survey_url}&request_id={request_id}"
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(full_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    file_path = QR_DIR / f'qr_request_{request_id}.png'
    img.save(file_path)
    
    _save_qr_to_database(request_id, str(file_path), full_url)
    return str(file_path)


def _save_qr_to_database(request_id, qr_path, survey_link):
    """Сохранить информацию о QR-коде в БД."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO quality_surveys (request_id, qr_code, survey_link)
        VALUES (?, ?, ?)
    ''', (request_id, qr_path, survey_link))
    connection.commit()
    connection.close()


def generate_qr_for_ready_requests():
    """Сгенерировать QR-коды для всех готовых заявок."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT request_id FROM requests WHERE request_status IN ('Готова к выдаче', 'Завершена')")
    request_ids = [row[0] for row in cursor.fetchall()]
    connection.close()
    
    count = 0
    for request_id in request_ids:
        try:
            generate_qr_code(request_id)
            count += 1
        except Exception as e:
            print(f"Ошибка генерации QR для заявки {request_id}: {e}")
    return count