#!/usr/bin/env python3
"""
Script de Configuração Inicial - EvidentlyAI Server

Este script ajuda a configurar o projeto EvidentlyAI Server automaticamente,
incluindo verificação de dependências, criação de diretórios e configurações iniciais.

Execute: python setup_project.py

Autor: Sua Equipe
Data: 2025
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform


class ProjectSetup:
    """Classe para configuração inicial do projeto."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def print_banner(self):
        """Exibir banner de boas-vindas."""
        print("🚀" + "="*60 + "🚀")
        print("    EVIDENTLY AI SERVER - CONFIGURAÇÃO INICIAL")
        print("🚀" + "="*60 + "🚀")
        print()
        print("Este script irá configurar automaticamente seu ambiente.")
        print("Certifique-se de ter Python 3.13+ e Docker instalados.")
        print()
    
    def check_python_version(self):
        """Verificar versão do Python."""
        print("🐍 Verificando versão do Python...")
        
        version = sys.version_info
        required_version = (3, 13)
        
        if version >= required_version:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
            return True
        else:
            self.errors.append(f"Python {required_version[0]}.{required_version[1]}+ é necessário")
            print(f"❌ Python {version.major}.{version.minor} - Versão insuficiente")
            return False
    
    def check_docker(self):
        """Verificar se Docker está instalado e rodando."""
        print("\n🐳 Verificando Docker...")
        
        try:
            # Verificar se Docker está instalado
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, text=True, check=True
            )
            print(f"✅ Docker instalado: {result.stdout.strip()}")
            
            # Verificar se Docker está rodando
            subprocess.run(
                ["docker", "ps"], 
                capture_output=True, text=True, check=True
            )
            print("✅ Docker está rodando")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append("Docker não está instalado ou rodando")
            print("❌ Docker não encontrado ou não está rodando")
            return False
    
    def check_docker_compose(self):
        """Verificar Docker Compose."""
        print("\n🔧 Verificando Docker Compose...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, text=True, check=True
            )
            print(f"✅ Docker Compose: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Tentar comando alternativo
                result = subprocess.run(
                    ["docker", "compose", "version"], 
                    capture_output=True, text=True, check=True
                )
                print(f"✅ Docker Compose (plugin): {result.stdout.strip()}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.warnings.append("Docker Compose não encontrado")
                print("⚠️  Docker Compose não encontrado")
                return False
    
    def check_make(self):
        """Verificar se Make está disponível."""
        print("\n🔨 Verificando Make...")
        
        try:
            subprocess.run(
                ["make", "--version"], 
                capture_output=True, text=True, check=True
            )
            print("✅ Make está disponível")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.warnings.append("Make não encontrado (opcional)")
            print("⚠️  Make não encontrado (opcional)")
            return False
    
    def create_directories(self):
        """Criar diretórios necessários."""
        print("\n📁 Criando diretórios...")
        
        directories = [
            "workspace",
            "reports", 
            "examples",
            "data",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Criado: {directory}/")
            else:
                print(f"✅ Existe: {directory}/")
    
    def create_env_file(self):
        """Criar arquivo .env se não existir."""
        print("\n⚙️  Configurando arquivo de ambiente...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / "env.example"
        
        if not env_file.exists():
            if env_example.exists():
                shutil.copy(env_example, env_file)
                print("✅ Arquivo .env criado a partir do env.example")
            else:
                # Criar .env básico
                env_content = """# Configurações básicas do EvidentlyAI Server
EVIDENTLY_SERVER_HOST=localhost
EVIDENTLY_SERVER_PORT=8000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
LOG_LEVEL=INFO
"""
                with open(env_file, 'w') as f:
                    f.write(env_content)
                print("✅ Arquivo .env básico criado")
        else:
            print("✅ Arquivo .env já existe")
    
    def check_virtual_environment(self):
        """Verificar se está em ambiente virtual."""
        print("\n🔧 Verificando ambiente virtual...")
        
        in_venv = (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if in_venv:
            print("✅ Ambiente virtual ativo")
            return True
        else:
            self.warnings.append("Recomendado usar ambiente virtual")
            print("⚠️  Não está em ambiente virtual (recomendado)")
            return False
    
    def install_dependencies(self):
        """Instalar dependências Python."""
        print("\n📦 Instalando dependências Python...")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."], 
                check=True,
                cwd=self.project_root
            )
            print("✅ Dependências instaladas com sucesso")
            return True
        except subprocess.CalledProcessError:
            self.errors.append("Erro ao instalar dependências Python")
            print("❌ Erro ao instalar dependências")
            return False
    
    def test_import_evidently(self):
        """Testar importação do Evidently."""
        print("\n🧪 Testando instalação do Evidently...")
        
        try:
            import evidently
            print(f"✅ Evidently {evidently.__version__} importado com sucesso")
            return True
        except ImportError:
            self.warnings.append("Evidently não pode ser importado")
            print("⚠️  Erro ao importar Evidently")
            return False
    
    def create_gitignore_entries(self):
        """Adicionar entradas ao .gitignore se necessário."""
        print("\n📋 Verificando .gitignore...")
        
        gitignore_path = self.project_root / ".gitignore"
        additional_entries = [
            "# EvidentlyAI Server específicos",
            "reports/",
            "logs/",
            "data/",
            "*.html",
            ".env",
            "__pycache__/",
            "*.pyc",
            "venv/",
        ]
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
            
            new_entries = []
            for entry in additional_entries:
                if entry not in content:
                    new_entries.append(entry)
            
            if new_entries:
                with open(gitignore_path, 'a') as f:
                    f.write("\n" + "\n".join(new_entries))
                print(f"✅ Adicionadas {len(new_entries)} entradas ao .gitignore")
            else:
                print("✅ .gitignore já está atualizado")
        else:
            with open(gitignore_path, 'w') as f:
                f.write("\n".join(additional_entries))
            print("✅ .gitignore criado")
    
    def show_next_steps(self):
        """Mostrar próximos passos."""
        print("\n" + "🎯" + "="*60 + "🎯")
        print("                    PRÓXIMOS PASSOS")
        print("🎯" + "="*60 + "🎯")
        
        print("\n1. 🚀 Inicializar o servidor:")
        if shutil.which("make"):
            print("   make run")
        else:
            print("   docker-compose up -d")
        
        print("\n2. 🔍 Verificar status:")
        if shutil.which("make"):
            print("   make status")
        else:
            print("   docker-compose ps")
        
        print("\n3. 🧪 Executar demonstração:")
        print("   python remote_demo_project.py")
        
        print("\n4. 🌐 Acessar serviços:")
        print("   - EvidentlyAI Dashboard: http://localhost:8000")
        print("   - MinIO Console: http://localhost:9001")
        print("     (usuário: minioadmin, senha: minioadmin123)")
        
        print("\n5. 📖 Ler documentação:")
        print("   - README.md - Documentação completa")
        print("   - GUIA_USO.md - Guia de uso rápido")
        
        print("\n💡 Dicas:")
        print("   - Use 'make help' para ver comandos disponíveis")
        print("   - Verifique examples/ para scripts prontos")
        print("   - Customize o .env conforme necessário")
    
    def show_summary(self):
        """Mostrar resumo da configuração."""
        print("\n" + "📋" + "="*60 + "📋")
        print("                    RESUMO DA CONFIGURAÇÃO")
        print("📋" + "="*60 + "📋")
        
        if not self.errors and not self.warnings:
            print("✅ Configuração concluída com sucesso!")
            print("✅ Todos os pré-requisitos atendidos")
        else:
            if self.errors:
                print("❌ Problemas encontrados:")
                for error in self.errors:
                    print(f"   - {error}")
            
            if self.warnings:
                print("⚠️  Avisos:")
                for warning in self.warnings:
                    print(f"   - {warning}")
        
        print(f"\n📊 Status:")
        print(f"   - Erros: {len(self.errors)}")
        print(f"   - Avisos: {len(self.warnings)}")
        
        if self.errors:
            print("\n💡 Resolva os erros antes de continuar.")
        else:
            print("\n🎉 Projeto pronto para uso!")
    
    def run_setup(self):
        """Executar configuração completa."""
        self.print_banner()
        
        # Verificações de sistema
        self.check_python_version()
        self.check_docker()
        self.check_docker_compose()
        self.check_make()
        
        # Configuração do projeto
        self.check_virtual_environment()
        self.create_directories()
        self.create_env_file()
        self.create_gitignore_entries()
        
        # Se não há erros críticos, instalar dependências
        if not self.errors:
            self.install_dependencies()
            self.test_import_evidently()
        
        # Resumo e próximos passos
        self.show_summary()
        
        if not self.errors:
            self.show_next_steps()
        
        return len(self.errors) == 0


def main():
    """Função principal."""
    setup = ProjectSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Setup concluído com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Setup falhou. Resolva os problemas e tente novamente.")
        sys.exit(1)


if __name__ == "__main__":
    main() 