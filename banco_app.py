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

# --- Função para validar CPF ---
def validar_cpf(cpf):
    # Remover caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)

    # Verificar se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Validar se o CPF não é uma sequência repetida (ex: 11111111111)
    if cpf == cpf[0] * len(cpf):
        return False

    # Validação do primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    digito1 = (soma * 10) % 11
    if digito1 == 10 or digito1 == 11:
        digito1 = 0
    if digito1 != int(cpf[9]):
        return False

    # Validação do segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    digito2 = (soma * 10) % 11
    if digito2 == 10 or digito2 == 11:
        digito2 = 0
    if digito2 != int(cpf[10]):
        return False

    return True

# --- Função para validar Email ---
def validar_email(email):
    regex_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex_email, email)

# --- Interface Streamlit ---
st.set_page_config(page_title="Banco Digital", layout="centered")
custom_title("🏦 Sistema Bancário Digital Simplificado")

# --- Se o usuário não estiver logado, exibe menu de login/cadastro ---
if not st.session_state.logged_user:
    menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"], label_visibility="collapsed")

    # Customizando o CSS para ocultar a caixa de texto no selectbox
    st.markdown(
        """
        <style>
        .css-1p4b5jv {
            pointer-events: none;
            opacity: 1;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # --- Cadastro de Usuário ---
    if menu == "Cadastro":
        custom_subheader("📋 Cadastro de Usuário")
        reg_name = st.text_input("Nome")
        reg_cpf = st.text_input("CPF")
        reg_email = st.text_input("Email")
        reg_password = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if find_user(reg_email):
                st.warning("Email já cadastrado.")
            elif any(u["cpf"] == reg_cpf for u in users):  # Verifica se o CPF já está cadastrado
                st.warning("CPF já cadastrado.")
            elif not (reg_name and reg_cpf and reg_email and reg_password):
                st.warning("Preencha todos os campos.")
            elif not validar_cpf(reg_cpf):
                st.warning("CPF inválido. Verifique o formato.")
            elif not validar_email(reg_email):
                st.warning("Email inválido. Verifique o formato.")
            else:
                users.append({
                    "id": len(users) + 1,
                    "name": reg_name,
                    "cpf": reg_cpf,
                    "email": reg_email,
                    "password": hash_password(reg_password)
                })
                st.success("Cadastro realizado com sucesso!")

    # --- Login de Usuário ---
    elif menu == "Login":
        custom_subheader("🔐 Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if lockout_check(login_email):
                st.error("Conta bloqueada por 5 minutos após 5 tentativas inválidas.")
            else:
                user = verify_login(login_email, login_password)
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
        value = st.number_input("Valor do depósito", min_value=0.01)
        if st.button("Confirmar Depósito"):
            record_transaction(user["id"], value, "depósito")
            st.success("Depósito realizado com sucesso!")

    elif page == "Sacar":
        custom_subheader("➖ Saque")
        value = st.number_input("Valor do saque", min_value=0.01)
        if st.button("Confirmar Saque"):
            if get_balance(user["id"]) >= value:
                record_transaction(user["id"], -value, "saque")
                st.success("Saque realizado com sucesso!")
            else:
                st.error("Saldo insuficiente.")

    elif page == "Transferir":
        custom_subheader("🔄 Transferência")
        dest_cpf = st.text_input("CPF do destinatário")
        value = st.number_input("Valor da transferência", min_value=0.01)
        if st.button("Confirmar Transferência"):
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
        custom_subheader("📄 Extrato de Movimentações")
        extrato = get_statement(user["id"])
        if extrato:
            for txn in extrato:
                st.write(f"{txn['date'].strftime('%d/%m/%Y %H:%M:%S')} - {txn['type'].capitalize()}: R$ {txn['amount']:.2f} - {txn['description']}")
        else:
            st.info("Nenhuma movimentação encontrada.")

    elif page == "Editar Perfil":
        custom_subheader("✏️ Editar Perfil")
        new_name = st.text_input("Novo Nome", value=user["name"])
        new_email = st.text_input("Novo Email", value=user["email"])
        current_password = st.text_input("Senha Atual", type="password")
        new_password = st.text_input("Nova Senha", type="password")

        if st.button("Salvar Alterações"):
            if user["password"] != hash_password(current_password):
                st.error("Senha atual incorreta.")
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
