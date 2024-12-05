import os
import sys
import threading

def read_passwords_from_dir(directory: str) -> dict:
    passwords = {}
    try:
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    passwords[file_name] = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Erro: Diretório não encontrado no caminho {directory}.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    return passwords

def rot13_obfuscation(password: str) -> str:
    return "".join(
        chr((ord(char) - 65 + 13) % 26 + 65) if char.isupper() else
        chr((ord(char) - 97 + 13) % 26 + 97) if char.islower() else char
        for char in password
    )

def process_file_and_write(file_name: str, file_path: str, passwords: list, semaphore: threading.Semaphore):
    """Process and overwrite the file with ROT13-obfuscated passwords."""
    obfuscated_passwords = [rot13_obfuscation(password) for password in passwords]

    try:
        # Adquirir o semáforo antes de acessar o arquivo
        with semaphore:
            with open(file_path, 'w') as file:
                file.write("\n".join(obfuscated_passwords) + "\n")
                print(f"Processed and updated file: {file_name}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo {file_path}: {e}")

def process_passwords_concurrently(directory: str, passwords_by_file: dict):
    threads = []
    semaphore = threading.Semaphore(4)  # Limitar a 4 threads simultâneas

    for file_name, passwords in passwords_by_file.items():
        file_path = os.path.join(directory, file_name)
        thread = threading.Thread(target=process_file_and_write, args=(file_name, file_path, passwords, semaphore))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <caminho_do_diretorio>")
        sys.exit(1)

    directory_path = sys.argv[1]

    passwords_by_file = read_passwords_from_dir(directory_path)

    process_passwords_concurrently(directory_path, passwords_by_file)