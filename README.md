# STS_Project
 ## **Projeto: Sistema Bancário Digital Simplificado**

**Grupo:** 

- Pedro Lucas Adorno (22.221.017-1)
- Guilherme Quirino (22.221.067-6)
- Bruna Borelli (22.121.119-6)

**Disciplina:** Simulação e Teste de Software (CC8550)

**Professor:** Luciano Rossi

**Centro Universitário FEI – 1º Semestre de 2025**

---

### **1. Introdução**

Uma aplicação básica de banco digital. O sistema permitirá que usuários realizem operações como cadastro, login, consulta de saldo, saques, depósitos, transferências e visualização de extrato. Esses requisitos serão usados na próxima etapa do projeto para o desenvolvimento e testes do sistema.

---

### **2. Requisitos Funcionais**

### **Requisito: Cadastro de Usuário**

- **ID:** RF01
- **Tipo:** Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Dependências:** Nenhuma
- **Origem:** Levantamento com o grupo
- **Descrição:** O sistema deve permitir que o usuário cadastre uma conta informando nome, CPF, e-mail e senha.
- **Critério de Aceitação:** Dados são salvos corretamente e o usuário recebe confirmação do cadastro.

---

### **Requisito: Login de Usuário**

- **ID:** RF02
- **Tipo:** Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Dependências:** RF01
- **Origem:** Grupo
- **Descrição:** O sistema deve permitir que o usuário entre com e-mail e senha cadastrados anteriormente.
- **Critério de Aceitação:** Acesso concedido com dados válidos e negado com dados inválidos.

---

### **Requisito: Consulta de Saldo**

- **ID:** RF03
- **Tipo:** Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Dependências:** RF02
- **Origem:** Grupo
- **Descrição:** Após o login, o cliente deve poder visualizar seu saldo atualizado.
- **Critério de Aceitação:** O valor do saldo é exibido corretamente conforme o histórico de movimentações.

---

### **Requisito: Depósito**

- **ID:** RF04
- **Tipo:** Funcional
- **Prioridade:** Média
- **Status:** Em Aberto
- **Dependências:** RF02
- **Origem:** Grupo
- **Descrição:** O cliente pode realizar um depósito informando o valor desejado.
- **Critério de Aceitação:** O valor do saldo aumenta corretamente e o depósito aparece no extrato.

---

### **Requisito: Saque**

- **ID:** RF05
- **Tipo:** Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Dependências:** RF02
- **Origem:** Grupo
- **Descrição:** O cliente pode realizar um saque, limitado ao valor disponível em saldo.
- **Critério de Aceitação:** O saldo é reduzido e o saque é registrado no extrato. Operação é bloqueada se saldo for insuficiente.

---

### **Requisito: Transferência entre Contas**

- **ID:** RF06
- **Tipo:** Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Dependências:** RF02 (Login), RF01 (Cadastro de Usuário)
- **Origem:** Grupo
- **Descrição:** O sistema deve permitir que um cliente transfira dinheiro para outra conta bancária dentro da própria plataforma, informando CPF ou número da conta de destino e o valor.
- **Critério de Aceitação:** O saldo do remetente é reduzido, o saldo do destinatário é aumentado e a operação é registrada no extrato de ambos.

---

### **Requisito: Consulta de Extrato**

- **ID:** RF07
- **Tipo:** Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Dependências:** RF02
- **Origem:** Grupo
- **Descrição:** O cliente deve poder visualizar um extrato contendo a lista das últimas movimentações (saques, depósitos, transferências), com data, valor e tipo de operação.
- **Critério de Aceitação:** O sistema exibe corretamente os dados ordenados por data, incluindo pelo menos as últimas 10 movimentações.

---

### **Requisito: Edição de Dados do Perfil**

- **ID:** RF08
- **Tipo:** Funcional
- **Prioridade:** Média
- **Status:** Em Aberto
- **Dependências:** RF02
- **Origem:** Grupo
- **Descrição:** O usuário pode editar seus dados de perfil (nome, e-mail e senha), sendo necessário informar a senha atual para confirmação.
- **Critério de Aceitação:** Dados são atualizados corretamente, e alterações são validadas com sucesso.

### **4. Requisitos Não Funcionais**

### **Requisito: Segurança de Senha**

- **ID:** RNF01
- **Tipo:** Não Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Origem:** Grupo
- **Descrição:** As senhas devem ser armazenadas de forma criptografada no banco de dados.
- **Critério de Aceitação:** Verificação do armazenamento criptografado por inspeção técnica.

---

### **Requisito: Bloqueio após Tentativas Inválidas**

- **ID:** RNF02
- **Tipo:** Não Funcional
- **Prioridade:** Média
- **Status:** Em Aberto
- **Origem:** Grupo
- **Descrição:** O sistema deve bloquear temporariamente o acesso de um usuário após 5 tentativas consecutivas de login com senha incorreta, impedindo novos acessos por um período de 5 minutos.
- **Critério de Aceitação:** Após a 5ª tentativa errada, o sistema exibe uma mensagem de bloqueio e impede novas tentativas até o tempo de espera ser concluído.

---

### **5. Requisito de Interface Gráfica**

### **Requisito: Painel do Cliente**

- **ID:** RIG01
- **Tipo:** Funcional
- **Prioridade:** Alta
- **Status:** Em Aberto
- **Origem:** Grupo
- **Descrição:** Após login, o usuário será direcionado para um painel com botões de "Ver saldo", "Depositar", "Sacar" e "Sair".
- **Critério de Aceitação:** Todos os botões funcionam corretamente e redirecionam para as telas apropriadas.
