# urlpo

استخرج كل الروابط من ملفات HTML / JS / CSS وحمّلها في مجلد `UrlPo`.

مصممة لـ **Termux** وقابلة للتثبيت عبر `pip`.

## تثبيت

```bash
# من GitHub (بعد الرفع)
pkg install git
```
```
git clone https://github.com/ibrahimkhacef5-del/UrlPo

```
```
# أو محلياً
pip install -e.
```

## استخدام

```bash
urlpo path/to/file.html
urlpo style.css -o MyDownloads
urlpo app.js -b https://example.com
```

### خيارات

| خيار | وصف |
|------|-----|
| `file` | مسار الملف (html / js / css) |
| `-o`, `--out` | مجلد الإخراج (افتراضي: `UrlPo`) |
| `-b`, `--base` | Base URL للروابط النسبية |
| `-w`, `--workers` | عدد التحميلات المتوازية |

## مثال برمجي

```python
from urlpo.core import process_file

result = process_file("index.html", out_dir="UrlPo")
print(result)
```

## متطلبات

- Python ≥ 3.8
- requests
- beautifulsoup4

---
MIT License
