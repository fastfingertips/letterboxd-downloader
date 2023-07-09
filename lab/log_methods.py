from constants import *
from inspect import currentframe #: PMI

def txtLog(r_message, log_file_path): #: None: Kullanıcı log lokasyonunu belirtmese de olur.
    try: ## Denenecek işlemler..
        with open(log_file_path, "a", encoding="utf-8") as f: #: Eklemek üzere bir dosya açar, mevcut değilse dosyayı oluşturur
            f.writelines(f'{r_message}\n')
    except Exception as e: print(f'Loglama işlemi {e} nedeniyle başarısız.')

def errorLine(e): #: Error Code generator
    cl = currentframe()
    # txtLog(f'{PRE_LOG_ERR} Error on line {cl.f_back.f_lineno} Exception Message: {e}',logFilePath)