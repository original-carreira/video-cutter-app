from services.obs_controller import OBSController
import time

print(">>> Iniciando teste OBS")

obs = OBSController(password="Sg@273220")  # use a sua senha real

try:
    print(">>> Conectando...")
    obs.connect()

    print(">>> Iniciando gravação")
    obs.start_recording()

    time.sleep(5)

    print(">>> Parando gravação")
    obs.stop_recording()

    print(">>> Desconectando")
    obs.disconnect()

    print(">>> Teste finalizado com sucesso!")

except Exception as e:
    print("ERRO:", e)