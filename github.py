import os

comando_email = "git config user.email \"20241pvai0030018@estudantes.ifpr.edu.br\" "
os.system(comando_email)

print("Aplicando modificações...")
comando1 = "git add *"
os.system(comando1)

mensagem = input("Mensagem do commit: ")
while(len(mensagem) < 5):
    print("Mensagem curta demais...")
    mensagem = input("Mensagem do commit: ")


print("Registrando...")
comando2 = "git commit -m" + mensagem
os.system(comando2)

comando3 = "git push"
os.system(comando3)