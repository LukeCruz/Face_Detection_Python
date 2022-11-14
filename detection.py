import imutils
import cv2
import dlib
import time
import multiprocessing
from imutils import face_utils
from scipy.spatial import distance

from notify_run import Notify 

from playsound import playsound
from utils import proporcao_dos_olhos, proporcao_da_face
from playsound import playsound

def inicio():
	
	# Tamanho da abertura dos olhos e posiçåo da face
	tamanho_do_olho = 0.15
	tamanho_da_face = 0.60

	# Posição do quadro de imagem
	posicao_do_olho_no_quadro = 5
	posicao_da_face_no_quadro = 5

    # chama função dentro da biblioteca DLIB
	detect = dlib.get_frontal_face_detector()

	# Modelo treinado com fotos do motorista ( IBM Watson )
	predict = dlib.shape_predictor("shape_face_lucas_training.dat")

	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
	(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["face"]

	# captura de video
	cap=cv2.VideoCapture(0)

	# marcacao dos olhos e face
	tamanho_inicial_dos_olhos=0
	posicao_inicial_da_face=0

	# calculo da distancia euclideana
	while True:
		ret, quadro=cap.read()
		quadro = imutils.resize(quadro, height = 600, width= 600)
		quadro_cinza = cv2.cvtColor(quadro, cv2.COLOR_BGR2quadro_cinza)
		objetos = detect(quadro_cinza, 0)
		for objeto in objetos:
			shape = predict(quadro_cinza, objeto)
			shape = face_utils.shape_to_np(shape)
			olho_esquerdo = shape[lStart:lEnd]
			olho_direito = shape[rStart:rEnd]
			face = shape[mStart:mEnd]
			esquerdo_EAR = proporcao_dos_olhos(olho_esquerdo)
			direito_EAR = proporcao_dos_olhos(olho_direito)
			ear = (esquerdo_EAR + direito_EAR) / 2.0
			olho_esquerdo_Hull = cv2.convexHull(olho_esquerdo)
			olho_direito_Hull = cv2.convexHull(olho_direito)
			face = proporcao_da_face(face)
			faceHull = cv2.convexHull(face)

			# desenho dos traços na face
			cv2.drawContours(quadro, [olho_esquerdo_Hull], -1, (0, 255, 0), 1)
			cv2.drawContours(quadro, [olho_direito_Hull], -1, (0, 255, 0), 1)
			cv2.drawContours(quadro, [face], -1, (255, 255, 255), 1)
			cv2.putText(quadro, "tamanho dos olhos: {}".format(ear), (5, 50),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
			cv2.putText(quadro, "tamanho da face: {}".format(face), (5, 80),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
	
			# Mensagem de alerta 
			if face > tamanho_da_face:
				posicao_inicial_da_face += 1
				if posicao_inicial_da_face >= posicao_da_face_no_quadro:
					cv2.putText(quadro, "RISCO DE ACIDENTE ", (10, 370),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
					cv2.putText(quadro, "sono {}".format(ear), (5, 50),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
					time.sleep(10)

					# Dispara um alarme sonoro e alarme visual 
					p = multiprocessing.Process(target=playsound, args=("Alarme.wav",))
					p.start()
					time.sleep(4)
					p.terminate()

					#Envia uma notificação via HTTP
					notify = Notify()
					notify.send("AJUDA ! MOTORISTA CAMINHAO 1 COM FADIGA ")
					
			else:
				posicao_inicial_da_face = 0

			# Comparação do threshold (tamanho_do_olho) com o tamanho dos olhos (ear)
			if ear < tamanho_do_olho:
				tamanho_inicial_dos_olhos += 1
				if tamanho_inicial_dos_olhos >= posicao_do_olho_no_quadro:
					cv2.putText(quadro, "MOTORISTA DORMINDO ", (10,400),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					time.sleep(10)
					p = multiprocessing.Process(target=playsound, args=("Alarme2.wav",))
					p.start()
					time.sleep(4)
					p.terminate()
					notify = Notify()
					notify.send("AJUDA ! MOTORISTA CAMINHAO 1 COM RISCO DE ACIDENTE ")
			else:
				tamanho_inicial_dos_olhos = 0
		
		# Quadro plotado
		cv2.imshow("Frame", quadro)

		# Aguardando fim
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break

	# fechar janelas
	cv2.destroyAllWindows()
	cap.stop()

def main():
	inicio()

if __name__ == '__main__':
	main()