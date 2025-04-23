import streamlit as st
import hashlib
import re
from datetime import datetime, timedelta

# --- Persistência usando session_state ---
if "users" not in st.session_state:
    st.session_state.users = []

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = {}

if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

if "menu" not in st.session_state:
    st.session_state.menu = "Login"

# --- Referências locais para facilitar ---
users = st.session_state.users
transactions = st.session_state.transactions
login_attempts = st.session_state.login_attempts

# --- Função personalizada para os titulos ---
def custom_subheader(text):
    html = f'<div style="font-size:24px; font-weight:600; margin-top:20px;">{text}</div>'
    st.markdown(html, unsafe_allow_html=True)

def custom_title(text):
    html = f'<div style="font-size: 36px; font-weight: 700; margin-bottom: 20px;">{text}</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- Funções auxiliares ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def find_user(email):
    return next((u for u in users if u["email"] == email), None)

def verify_login(email, password):
    user = find_user(email)
    if user and user["password"] == hash_password(password):
        return user
    return None

def get_balance(user_id):
    return sum(txn["amount"] for txn in transactions if txn["user_id"] == user_id)

def get_statement(user_id):
    return [txn for txn in transactions if txn["user_id"] == user_id][-10:][::-1]

def record_transaction(user_id, amount, txn_type, description=""):
    transactions.append({
        "user_id": user_id,
        "amount": amount,
        "type": txn_type,
        "description": description,
        "date": datetime.now()
    })

def lockout_check(email):
    data = login_attempts.get(email)
    return data and data["count"] >= 5 and datetime.now() < data["blocked_until"]

def record_login_attempt(email, success):
    data = login_attempts.get(email, {"count": 0, "blocked_until": None})
    if success:
        login_attempts[email] = {"count": 0, "blocked_until": None}
    else:
        data["count"] += 1
        if data["count"] >= 5:
            data["blocked_until"] = datetime.now() + timedelta(minutes=5)
        login_attempts[email] = data

def validar_cpf(cpf):
    if not re.fullmatch(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
        return False
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * len(cpf):
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10: digito1 = 0
    if digito1 != int(cpf[9]): return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10: digito2 = 0
    return digito2 == int(cpf[10])

def validar_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)

def validar_nome(nome):
    return re.fullmatch(r"[A-Za-zÀ-ÿ\s]{2,}", nome.strip()) is not None

# --- Interface Streamlit ---
st.set_page_config(page_title="Banco Digital", layout="centered")
custom_title("🏦 Sistema Bancário Digital Simplificado")

# --- Menu principal (Login ou Cadastro) ---
if not st.session_state.logged_user:
    st.session_state.menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"], index=["Login", "Cadastro"].index(st.session_state.menu), label_visibility="collapsed")

    st.markdown("""
        <style>
        .css-1p4b5jv {
            pointer-events: none;
            opacity: 1;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.menu == "Cadastro":
        custom_subheader("📋 Cadastro de Usuário")

        if "reg_name" not in st.session_state:
            st.session_state.reg_name = ""
        if "reg_cpf" not in st.session_state:
            st.session_state.reg_cpf = ""
        if "reg_email" not in st.session_state:
            st.session_state.reg_email = ""
        if "reg_password" not in st.session_state:
            st.session_state.reg_password = ""

        reg_name = st.text_input("Nome", value=st.session_state.reg_name)
        reg_cpf = st.text_input("CPF (Formato: xxx.xxx.xxx-xx)", value=st.session_state.reg_cpf)
        reg_email = st.text_input("Email", value=st.session_state.reg_email)
        reg_password = st.text_input("Senha", type="password", value=st.session_state.reg_password)

        st.session_state.reg_name = reg_name
        st.session_state.reg_cpf = reg_cpf
        st.session_state.reg_email = reg_email
        st.session_state.reg_password = reg_password

        if st.button("Cadastrar"):
            if find_user(reg_email):
                st.warning("Email já cadastrado.")
            elif not validar_nome(reg_name):
                st.warning("Nome inválido.")
            elif any(u["cpf"] == reg_cpf for u in users):
                st.warning("CPF já cadastrado.")
            elif not (reg_name and reg_cpf and reg_email and reg_password):
                st.warning("Preencha todos os campos.")
            elif not validar_cpf(reg_cpf):
                st.warning("CPF inválido.")
            elif not validar_email(reg_email):
                st.warning("Email inválido.")
            else:
                users.append({
                    "id": len(users) + 1,
                    "name": reg_name.lower(),
                    "cpf": reg_cpf,
                    "email": reg_email.lower(),
                    "password": hash_password(reg_password)
                })
                st.success("Cadastro realizado com sucesso!")
                st.session_state.reg_name = ""
                st.session_state.reg_cpf = ""
                st.session_state.reg_email = ""
                st.session_state.reg_password = ""

                # Limpa os campos de login
                st.session_state.login_email = ""
                st.session_state.login_password = ""

                # Redireciona para tela de login
                st.session_state.menu = "Login"
                st.rerun()

    elif st.session_state.menu == "Login":
        custom_subheader("🔐 Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if lockout_check(login_email):
                st.error("Conta bloqueada por 5 minutos após 5 tentativas inválidas.")
            else:
                user = verify_login(login_email.lower(), login_password)
                record_login_attempt(login_email, user is not None)
                if user:
                    st.session_state.logged_user = user
                    st.success(f"Bem-vindo, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos.")

# --- Painel do Cliente ---
if st.session_state.logged_user:
    user = st.session_state.logged_user
    st.sidebar.markdown(f"**Logado como:** {user['name']}")
    page = st.sidebar.radio("Painel", ["Ver Saldo", "Depositar", "Sacar", "Transferir", "Extrato", "Editar Perfil", "Sair"])

    if page == "Ver Saldo":
        custom_subheader("💰 Saldo Atual")
        st.success(f"R$ {get_balance(user['id']):.2f}")

    elif page == "Depositar":
        custom_subheader("➕ Depósito")
        value = st.number_input("Valor do depósito", min_value=0.00)
        if st.button("Confirmar Depósito"):
            if value < 0.01:
                st.error("Valor inválido.")
            else:
                record_transaction(user["id"], value, "depósito")
                st.success("Depósito realizado!")

    elif page == "Sacar":
        custom_subheader("➖ Saque")
        value = st.number_input("Valor do saque", min_value=0.00)
        if st.button("Confirmar Saque"):
            if value < 0.01:
                st.error("Valor inválido.")
            elif get_balance(user["id"]) < value:
                st.error("Saldo insuficiente.")
            else:
                record_transaction(user["id"], -value, "saque")
                st.success("Saque realizado!")

    elif page == "Transferir":
        custom_subheader("🔄 Transferência")
        dest_cpf = st.text_input("CPF do destinatário")
        value = st.number_input("Valor da transferência", min_value=0.00)
        if st.button("Confirmar Transferência"):
            if value < 0.01:
                st.error("Valor inválido.")
            else:
                recipient = next((u for u in users if u["cpf"] == dest_cpf), None)
                if not recipient:
                    st.error("Destinatário não encontrado.")
                elif get_balance(user["id"]) < value:
                    st.error("Saldo insuficiente.")
                else:
                    record_transaction(user["id"], -value, "transferência", f"Para {recipient['name']}")
                    record_transaction(recipient["id"], value, "transferência", f"De {user['name']}")
                    st.success("Transferência realizada com sucesso!")

    elif page == "Extrato":
        custom_subheader("📄 Extrato")
        extrato = get_statement(user["id"])
        if extrato:
            for txn in extrato:
                st.write(f"{txn['date'].strftime('%d/%m/%Y %H:%M')} - {txn['type'].capitalize()}: R$ {txn['amount']:.2f} - {txn['description']}")
        else:
            st.info("Nenhuma transação registrada.")

    elif page == "Editar Perfil":
        custom_subheader("✏️ Editar Perfil")
        new_name = st.text_input("Novo Nome", value=user["name"])
        new_email = st.text_input("Novo Email", value=user["email"])
        current_password = st.text_input("Senha Atual", type="password")
        new_password = st.text_input("Nova Senha", type="password")

        if st.button("Salvar Alterações"):
            if not new_name.strip() or not new_email.strip():
                st.warning("Nome e email são obrigatórios.")
            elif user["password"] != hash_password(current_password):
                st.error("Senha atual incorreta.")
            elif not validar_nome(new_name):
                st.error("Nome inválido.")
            elif new_email != user["email"] and find_user(new_email):
                st.warning("Email já cadastrado.")
            elif not validar_email(new_email):
                st.warning("Email inválido. Verifique o formato.")
            elif new_password and current_password == new_password:
                st.warning("Senha nova não pode ser igual a anterior.")
            else:
                user["name"] = new_name
                user["email"] = new_email
                if new_password:
                    user["password"] = hash_password(new_password)
                st.success("Perfil atualizado com sucesso!")

    elif page == "Sair":
        st.session_state.logged_user = None
        st.success("Logout realizado.")
        st.rerun()
