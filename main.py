import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import zlib

ctk.set_appearance_mode("System")  # ou "Light", "Dark"
ctk.set_default_color_theme("blue")

def ler_mensagem_arquivo(caminho_txt):
    with open(caminho_txt, 'r', encoding='utf-8') as f:
        return f.read()

def esconder_mensagem(imagem_origem, mensagem, imagem_saida):
    # Compacta a mensagem
    mensagem_comprimida = zlib.compress(mensagem.encode('utf-8'))

    # Adiciona prefixo com tamanho da mensagem comprimida (4 bytes)
    tamanho = len(mensagem_comprimida)
    tamanho_bytes = tamanho.to_bytes(4, byteorder='big')
    dados_para_inserir = tamanho_bytes + mensagem_comprimida

    # Transforma em binário
    mensagem_bin = ''.join(f'{byte:08b}' for byte in dados_para_inserir)

    img = Image.open(imagem_origem).convert("RGB")
    pixels = img.load()
    largura, altura = img.size

    capacidade_bits = largura * altura
    if len(mensagem_bin) > capacidade_bits:
        return False  # imagem pequena demais

    idx = 0
    for y in range(altura):
        for x in range(largura):
            if idx < len(mensagem_bin):
                r, g, b = pixels[x, y]
                b = (b & ~1) | int(mensagem_bin[idx])
                pixels[x, y] = (r, g, b)
                idx += 1
            else:
                img.save(imagem_saida, format='PNG', compress_level=0, optimize=False)
                return True

    # Se terminou exatamente no último pixel
    img.save(imagem_saida, format='PNG', compress_level=0, optimize=False)
    return True

class EsteganografiaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Criador de Mensagem Oculta")
        self.geometry("700x500")

        self.imagem_path = None

        self.label_imagem = ctk.CTkLabel(self, text="Imagem PNG:", font=ctk.CTkFont(size=14))
        self.label_imagem.pack(pady=10)

        self.botao_imagem = ctk.CTkButton(self, text="Selecionar Imagem PNG", command=self.selecionar_imagem)
        self.botao_imagem.pack(pady=5)

        self.label_mensagem = ctk.CTkLabel(self, text="Mensagem a ser escondida:", font=ctk.CTkFont(size=14))
        self.label_mensagem.pack(pady=10)

        self.text_mensagem = ctk.CTkTextbox(self, width=600, height=200)
        self.text_mensagem.pack(pady=5)

        self.botao_arquivo_txt = ctk.CTkButton(self, text="Importar de arquivo .txt", command=self.carregar_txt)
        self.botao_arquivo_txt.pack(pady=5)

        self.botao_esconder = ctk.CTkButton(self, text="Esconder Mensagem e Salvar Imagem", command=self.salvar_imagem)
        self.botao_esconder.pack(pady=20)

    def selecionar_imagem(self):
        caminho = filedialog.askopenfilename(filetypes=[("Imagens PNG", "*.png")])
        if caminho:
            self.imagem_path = caminho
            messagebox.showinfo("Imagem Selecionada", f"Imagem carregada:\n{os.path.basename(caminho)}")

    def carregar_txt(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
        if caminho:
            mensagem = ler_mensagem_arquivo(caminho)
            self.text_mensagem.delete("1.0", "end")
            self.text_mensagem.insert("1.0", mensagem)

    def salvar_imagem(self):
        if not self.imagem_path:
            messagebox.showerror("Erro", "Selecione uma imagem PNG primeiro.")
            return

        mensagem = self.text_mensagem.get("1.0", "end").strip()
        if not mensagem:
            messagebox.showerror("Erro", "Digite ou importe uma mensagem.")
            return

        caminho_saida = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("Imagem PNG", "*.png")],
                                                     title="Salvar imagem com mensagem")

        if caminho_saida:
            sucesso = esconder_mensagem(self.imagem_path, mensagem, caminho_saida)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Mensagem escondida com sucesso em:\n{caminho_saida}")
            else:
                messagebox.showerror("Erro", "Imagem muito pequena para conter toda a mensagem.")

# Executa a interface
if __name__ == "__main__":
    app = EsteganografiaApp()
    app.mainloop()