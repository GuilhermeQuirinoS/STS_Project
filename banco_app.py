import streamlit as st
import hashlib
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

# --- Interface Streamlit ---
st.set_page_config(page_title="Banco Digital", layout="centered")
st.title("🏦 Sistema Bancário Digital Simplificado")

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])

# --- Cadastro de Usuário ---
if menu == "Cadastro":
    st.subheader("📋 Cadastro de Usuário")
    reg_name = st.text_input("Nome")
    reg_cpf = st.text_input("CPF")
    reg_email = st.text_input("Email")
    reg_password = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        if find_user(reg_email):
            st.warning("Email já cadastrado.")
        elif not (reg_name and reg_cpf and reg_email and reg_password):
            st.warning("Preencha todos os campos.")
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
    st.subheader("🔐 Login")
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
            else:
                st.error("Email ou senha inválidos.")

# --- Painel do Cliente ---
if st.session_state.logged_user:
    user = st.session_state.logged_user
    st.sidebar.markdown(f"**Logado como:** {user['name']}")
    page = st.sidebar.radio("Painel", ["Ver Saldo", "Depositar", "Sacar", "Transferir", "Extrato", "Editar Perfil", "Sair"])

    if page == "Ver Saldo":
        st.subheader("💰 Saldo Atual")
        st.success(f"R$ {get_balance(user['id']):.2f}")

    elif page == "Depositar":
        st.subheader("➕ Depósito")
        value = st.number_input("Valor do depósito", min_value=0.01)
        if st.button("Confirmar Depósito"):
            record_transaction(user["id"], value, "depósito")
            st.success("Depósito realizado com sucesso!")

    elif page == "Sacar":
        st.subheader("➖ Saque")
        value = st.number_input("Valor do saque", min_value=0.01)
        if st.button("Confirmar Saque"):
            if get_balance(user["id"]) >= value:
                record_transaction(user["id"], -value, "saque")
                st.success("Saque realizado com sucesso!")
            else:
                st.error("Saldo insuficiente.")

    elif page == "Transferir":
        st.subheader("🔄 Transferência")
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
        st.subheader("📄 Extrato de Movimentações")
        extrato = get_statement(user["id"])
        if extrato:
            for txn in extrato:
                st.write(f"{txn['date'].strftime('%d/%m/%Y %H:%M:%S')} - {txn['type'].capitalize()}: R$ {txn['amount']:.2f} - {txn['description']}")
        else:
            st.info("Nenhuma movimentação encontrada.")

    elif page == "Editar Perfil":
        st.subheader("✏️ Editar Perfil")
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
