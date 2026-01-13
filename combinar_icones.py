#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
import os

def combinar_icones():
    """
    Combina os ícones em um único arquivo .ico com múltiplas resoluções
    """
    try:
        # Caminhos dos ícones (todos os tamanhos disponíveis)
        icones = [
            "resources/icone32.ico",
            "resources/icone48.ico", 
            "resources/icone64.ico",
            "resources/icone72.ico",
            "resources/icone96.ico"
        ]
        icone_saida = "resources/icone_completo.ico"
        
        # Lista para armazenar as imagens
        imagens = []
        
        # Carregar todos os ícones disponíveis
        for icone_path in icones:
            if os.path.exists(icone_path):
                with Image.open(icone_path) as img:
                    imagens.append(img.copy())
                    print(f"✓ Ícone carregado: {icone_path} - Tamanho: {img.size}")
        
        # Se não encontrou nenhum ícone, criar um padrão
        if not imagens:
            print("❌ Nenhum ícone encontrado!")
            return False
        
        # Salvar como arquivo .ico com múltiplas resoluções
        # Usar o primeiro ícone como base e adicionar todos os outros
        imagens[0].save(
            icone_saida,
            format='ICO',
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (72, 72), (96, 96), (128, 128), (256, 256)],
            append_images=imagens[1:] if len(imagens) > 1 else []
        )
        
        print(f"✓ Ícone combinado criado: {icone_saida}")
        print(f"✓ Total de resoluções incluídas: {len(imagens)}")
        print("✓ O arquivo contém múltiplas resoluções para melhor compatibilidade")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao combinar ícones: {e}")
        return False

if __name__ == "__main__":
    print("Combinando ícones...")
    if combinar_icones():
        print("\n✅ Processo concluído com sucesso!")
        print("Agora você pode usar o arquivo 'resources/icone_completo.ico' no PyInstaller")
    else:
        print("\n❌ Falha no processo!") 