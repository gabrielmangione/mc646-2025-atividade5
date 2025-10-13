# UNIVERSIDADE ESTADUAL DE CAMPINAS
## INSTITUTO DE COMPUTAÇÃO
### Atividade 4
### Testes Estruturais
#### MC646 - Verificação, Validação e Testes de Software

---

### 1 Descrição Geral

Essa atividade tem como foco a análise e geração de testes estruturais. Para isso, utilizaremos o projeto em Python presente nesse [repositório do Github](https://github.com/example). Este projeto contém 3 funcionalidades distintas, as quais estão descritas detalhadamente nesse documento. Cada grupo deverá:

*   Gerar um grafo de fluxo de controle para a lógica principal de cada funcionalidade e analisá-lo identificando declaração, definição/redefinição e uso (c-uso/p-uso).
*   Propor a criação de casos de teste buscando a máxima cobertura critérios todas-arestas e todos-uso.
*   Fazer a implementação dos testes no projeto de Python usando `pytest`
*   Gerar um relatório de cobertura com a lib `pytest-cov`

#### 1.1 Observações

*   Dentro do README possuem as instruções para a geração dos grafos de fluxo de controle e dados a partir de um script na raiz e um tutorial de como usar as flags do pytest para gerar o report de cobertura.
*   Para o funcionamento da geração das imagens é preciso o módulo Graphviz
*   Para ser possível rodar o ambiente basta instalar as bibliotecas dentro de `requirements.txt` e fazer instalar a pasta `src` como pacote. Comandos presentes no README

---

### 2 Funcionalidades

#### 2.1 Sistema de Detecção de Fraude de Cartão de Crédito

##### 2.1.1 Descrição

Este sistema é responsável por detectar transações potencialmente fraudulentas em tempo real. Ele analisa um conjunto de critérios, incluindo valor da transação, frequência das transações, mudanças de localização e o uso de listas de restrição (blacklists) para determinar se uma transação deve ser marcada como fraudulenta, exigir verificação ou bloquear o cartão. Adicionalmente, ele calcula uma pontuação de risco para cada transação, fornecendo uma medida mais detalhada de suspeita.

##### 2.1.2 Domínio de Entrada

*   **Valor da Transação:** double (ex: 15000.00)
*   **Horário da Transação:** LocalDateTime (ex: 2024-10-01T12:00:00)
*   **Local da Transação:** String (ex: "EUA", "França", "País de Alto Risco")
*   **Transações Anteriores:** Lista de transações (valor, horário, local)
*   **Locais em Lista de Restrição:** Lista de locais (ex: "País de Alto Risco")

##### 2.1.3 Saída

*   **Indicador de Fraude (Fraud Flag):** boolean (indica se a transação é considerada fraudulenta)
*   **Status de Bloqueio (Blocked Status):** boolean (indica se o cartão está bloqueado)
*   **Verificação Necessária (Verification Required):** boolean (indica se a transação requer verificação adicional)
*   **Pontuação de Risco (Risk Score):** int (0-100, mede o nível de risco da transação)

##### 2.1.4 Regras

1.  **Valor Elevado da Transação:** Se o valor da transação exceder um limiar configurável (ex: $10.000), a transação é marcada como potencialmente fraudulenta, exigindo verificação adicional, e a pontuação de risco aumenta em 50.
2.  **Transações Excessivas em Curto Período de Tempo:** Se mais de 10 transações ocorrerem em um período de 1 hora, o cartão é temporariamente bloqueado por razões de segurança. Isso impede transações futuras até que o titular do cartão seja contatado ou o bloqueio seja removido manualmente, e a pontuação de risco aumenta em 30.
3.  **Mudança de Localização em Curto Período de Tempo:** Se uma transação ocorrer em uma localização geográfica diferente da transação anterior e dentro de um curto período de tempo (ex: 30 minutos), a transação é marcada como potencialmente fraudulenta e requer verificação, e a pontuação de risco aumenta em 20.
4.  **Verificação de Lista de Restrição (Blacklist):** Transações originadas de locais em listas de restrição (ex: países conhecidos por altos níveis de fraude) resultam automaticamente no bloqueio do cartão, independentemente do valor da transação ou de outros fatores, e a pontuação de risco é definida como 100.
5.  **Cálculo da Pontuação de Risco:** A cada transação é atribuída uma pontuação de risco de 0 a 100, com base em vários fatores como valor, horário, frequência e mudanças de localização. Pontuações mais altas indicam maior risco, ajudando a priorizar investigações.

#### 2.2 Sistema de Reserva de Voos

##### 2.2.1 Descrição

Este sistema de reserva lida com cenários para reservas de voos. Ele implementa precificação dinâmica baseada na disponibilidade de assentos, demanda de mercado, descontos para grupos e taxas de reserva de última hora. Além disso, o sistema suporta cancelamentos com políticas de reembolso variáveis e o uso de pontos de recompensa para passageiros frequentes.

##### 2.2.2 Domínio de Entrada

*   **Número de Passageiros:** int (ex: 2, 5)
*   **Horário da Reserva:** LocalDateTime (ex: 2024-10-01T12:00:00)
*   **Horário de Partida:** LocalDateTime (ex: 2024-10-02T12:00:00)
*   **Disponibilidade de Assentos:** int (ex: 100)
*   **Preço Atual:** double (ex: 500.00)
*   **Vendas Anteriores:** int (ex: 50 assentos vendidos)
*   **É um Cancelamento (Is Cancellation):** boolean (indica se a reserva é um cancelamento)
*   **Pontos de Recompensa (Reward Points):** int (ex: 5000 pontos)

##### 2.2.3 Saída

*   **Confirmação da Reserva:** boolean (indica se a reserva foi bem-sucedida)
*   **Preço Total:** double (preço final após precificação dinâmica, descontos, taxas e pontos de recompensa)
*   **Valor do Reembolso:** double (valor do reembolso em caso de cancelamento)
*   **Pontos Utilizados:** boolean (indica se pontos de recompensa foram usados na reserva)

##### 2.2.4 Regras

1.  **Disponibilidade de Assentos:** As reservas só são confirmadas se houver assentos suficientes disponíveis no voo. Se não houver assentos suficientes, a reserva é rejeitada.
2.  **Precificação Dinâmica:** A forma de calcular o preço base final é baseada no preço atual por número de passageiros e um fator de preço, que é calculado da seguinte forma: (vendasAnteriores/100.0) × 0.8.
3.  **Taxa de Última Hora:** Se um cliente reservar um voo menos de 24 horas antes da partida, uma taxa especial de última hora de $100 é aplicada à tarifa total.
4.  **Desconto para Grupo:** Para reservas de grupos com mais de 4 passageiros, um desconto de 5% é aplicado à tarifa total.
5.  **Resgate de Pontos de Recompensa:** Passageiros frequentes podem resgatar pontos de recompensa para reduzir o preço de suas passagens. Cada ponto reduz a tarifa em $0,01 (1 centavo).
6.  **Política de Cancelamento:** Cancelamentos feitos mais de 48 horas antes da partida recebem reembolso total. Cancelamentos feitos dentro de 48 horas da partida recebem apenas 50% de reembolso.

#### 2.3 Sistema Inteligente de Gestão de Energia

##### 2.3.1 Descrição

O Sistema Inteligente de Gestão de Energia controla o uso de energia em uma casa inteligente, gerenciando dispositivos com base em condições atuais como preços da energia, hora do dia, temperatura e limites de uso. O sistema opera sob várias regras bem definidas, que devem ser seguidas pelos estudantes ao criar testes.

##### 2.3.2 Domínio de Entrada

*   **Preço da Energia em Tempo Real:** double (ex: 0.15 por kWh)
*   **Limiar de Preço da Energia:** double (ex: 0.20 por kWh)
*   **Prioridades dos Dispositivos:** Map<String, Integer> (ex: "Aquecimento"=1, "Luzes"=2, "Eletrodomésticos"=3)
*   **Hora Atual:** LocalDateTime (ex: 2024-10-01T12:00:00)
*   **Temperatura Atual:** double (ex: 21.5 graus Celsius)
*   **Faixa de Temperatura Desejada:** double[] (ex: [20.0, 24.0] graus Celsius)
*   **Limites de Uso de Energia:** double (ex: 30 kWh por dia)
*   **Total de Energia Usada Hoje:** double (ex: 25 kWh)
*   **Dispositivos Agendados:** List<DeviceSchedule> (ex: [Dispositivo: "Forno", Horário: 18:00])

##### 2.3.3 Saída

*   **Status dos Dispositivos:** Map<String, Boolean> (ex: "Aquecimento"=true, "Luzes"=false, "Eletrodomésticos"=false)
*   **Modo de Economia de Energia:** boolean (indica se o modo de economia de energia está ativo)
*   **Regulação de Temperatura:** boolean (indica se o aquecimento/resfriamento está ativo)
*   **Total de Energia Utilizada:** double (total de energia utilizada atualizado)

##### 2.3.4 Regras

1.  **Modo de Economia de Energia Baseado no Limiar de Preço:** Quando o preço atual da energia excede o limiar definido pelo usuário, o sistema entra em modo de economia de energia. Neste modo, o sistema desliga todos os dispositivos de baixa prioridade e mantém os de alta prioridade ativos para conservar energia. Dispositivos com prioridade maior que 1 são considerados de baixa prioridade.
2.  **Modo Noturno (Entre 23:00 e 06:00):** Das 23:00 às 06:00, o sistema ativa o modo noturno. Neste modo, apenas dispositivos essenciais como "Segurança" e "Geladeira" permanecem ligados. Todos os dispositivos não essenciais são desligados, independentemente de sua prioridade.
3.  **Regulação de Temperatura:** O sistema regula a temperatura ligando o sistema de aquecimento ou refrigeração com base na temperatura interna atual em relação a uma faixa definida pelo usuário. A regulação está ativa se a temperatura atual estiver fora da faixa desejada. Se estiver abaixo, liga o aquecimento; se estiver acima, liga a refrigeração.
4.  **Limite de Consumo de Energia:** Se o consumo total de energia do dia estiver se aproximando ou excedendo o limite diário definido pelo usuário, o sistema desliga progressivamente os dispositivos de baixa prioridade para se manter dentro do limite. Dispositivos com prioridade maior que 1 são desligados progressivamente. Dispositivos de alta prioridade (prioridade 1) são desligados por último, apenas quando necessário.
5.  **Dispositivos Agendados:** O sistema permite que os usuários agendem dispositivos para serem ligados em horários específicos. Se a hora atual corresponder à hora agendada para um dispositivo, o sistema liga o dispositivo independentemente de sua prioridade ou do status do modo de economia de energia. Os dispositivos agendados podem sobrepor os modos de economia de energia e noturno.

---

### 3 Entrega

*   O trabalho deve ser apresentado com um relatório em PDF contendo
    *   Relatório em PDF contendo os grafos de fluxo de controle de dados e a identificação, declaração, definição/redefinição, uso (c-uso e p-uso). Os métodos que devem ser analisados são: `manage_energy`, `book_flight` e `check_for_fraud`
    *   Propor casos de teste baseados no item anterior buscando a cobertura máxima seguindo os critérios todas-arestas e todos-uso (pares definição-uso em caminho livre de definição) explicando como cada caso de teste contribui na cobertura. Caso existam requisitos inalcançáveis, identificar os requisitos e explicar o motivo de ser inalcançável.
    *   Mostrar o relatório de cobertura gerado a partir do `pytest --cov` para os testes criados. Em casos de discrepância entre o relatório e o que foi previsto de cobertura anteriormente, detalhar o porquê e onde essa discrepância aconteceu.
    *   Link de um fork do Github contendo o repositório com a implementação dos casos testes criados para os métodos mencionados no primeiro item.
*   A entrega da atividade deve ser realizada exclusivamente via Classroom e entregue uma submissão por grupo
*   O documento entregue deve ter uma subdivisão das partes exigidas e de forma organizada
*   Se necessário, figuras podem ser enviadas separadamente como arquivos, só é necessário referenciar adequadamente no relatório
*   O nome do arquivo deve se chamar {Nome do Grupo}\_Atividade4.pdf
*   **Prazo de Entrega: 13/10/2025**

---

### 4 Avaliação

*   Entrega realizada dentro do prazo estipulado;
*   Geração correta e análise dos três grafo de fluxo de controle e dados;
*   Qualidade do relatório enviado descrevendo os testes e a estratégia adotada.
*   Qualidade dos testes criados
*   Geração do report de cobertura e qualidade análise em casos que ela não for total

---

### 5 Estrutura do Repositório

A estrutura do repositório é a seguinte:

```
mc646-2025-atividade4/
|-- .gitignore
|-- generate_graph.py
|-- pyproject.toml
|-- README.md
|-- requirements.txt
|-- run.py
|-- src/
|   |-- __init__.py
|   |-- energy/
|   |   |-- __init__.py
|   |   |-- DeviceSchedule.py
|   |   |-- EnergyManagementResult.py
|   |   |-- EnergyManagementSystem.py
|   |-- flight/
|   |   |-- __init__.py
|   |   |-- BookingResult.py
|   |   |-- FlightBookingSystem.py
|   |-- fraud/
|   |   |-- __init__.py
|   |   |-- FraudCheckResult.py
|   |   |-- FraudDetectionSystem.py
|   |   |-- Transaction.py
|-- tests/
    |-- test_device_schedule.py
```