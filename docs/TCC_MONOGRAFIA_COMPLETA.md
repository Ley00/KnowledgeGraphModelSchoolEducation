# SISTEMA PREDITIVO PARA APOIO À DECISÃO PEDAGÓGICA A PARTIR DE DADOS ESCOLARES

## Uma abordagem de análise temporal com aprendizado de máquina para previsão de notas e geração de alertas escolares

Autor: Warley [preencher sobrenome completo]  
Curso: [preencher curso]  
Instituição: [preencher instituição]  
Orientador(a): [preencher nome]  
Cidade: [preencher cidade]  
Ano: 2026

---

## FOLHA DE ROSTO

Warley [preencher sobrenome completo]

**Sistema preditivo para apoio à decisão pedagógica a partir de dados escolares: uma abordagem de análise temporal com aprendizado de máquina para previsão de notas e geração de alertas escolares**

Trabalho de Conclusão de Curso apresentado ao curso de [preencher curso], da [preencher instituição], como requisito parcial para obtenção do título de [preencher título].

Orientador(a): [preencher nome]

[Cidade]  
2026

---

## RESUMO

Este Trabalho de Conclusão de Curso apresenta o desenvolvimento de um sistema preditivo voltado ao contexto escolar, com foco na antecipação de dificuldades acadêmicas e no apoio à tomada de decisão de professores, coordenação pedagógica e secretaria. O problema central investigado consiste em verificar se dados escolares históricos, como notas, faltas, pagamentos e informações acadêmicas, podem ser integrados em uma pipeline analítica capaz de prever a próxima nota do aluno e identificar sinais de risco pedagógico antes da ocorrência de reprovação ou queda severa de desempenho. O projeto teve início com uma abordagem baseada em grafos, motivada pela natureza relacional do domínio escolar, mas evoluiu para uma estratégia tabular temporal após sucessivas análises indicarem maior aderência entre o problema e modelos supervisionados aplicados a dados longitudinais. A solução final foi estruturada como uma pipeline reprodutível composta por manutenção e anonimização do banco de dados, extração de dados, integração de múltiplas fontes, engenharia de atributos, validação temporal, seleção automática de modelos, análise de erro e geração de relatórios operacionais. Foram comparadas abordagens de baseline, Random Forest e HistGradientBoosting, tanto para regressão da próxima nota quanto para classificação de risco de nota inferior a 6,0. Os resultados mostraram que, para previsão numérica da próxima nota, o melhor cenário foi obtido com histórico mínimo de uma observação por disciplina, alcançando MAE de 0,7601 e superando o baseline simples baseado na última nota. Para alerta de risco, o melhor cenário ocorreu com histórico mínimo de duas observações, alcançando F1 de 0,7437, com recall de 0,8618 no teste temporal. Além da modelagem preditiva, foi desenvolvida uma camada de relatórios escolares com saídas específicas para professor, coordenação e secretaria, incluindo um ranking executivo de alunos prioritários. Como contribuição principal, o trabalho demonstra que uma arquitetura analítica temporal, orientada ao uso institucional e acompanhada de mecanismos de interpretação e priorização, é mais adequada ao contexto escolar do que abordagens isoladas de classificação ou exploração relacional. Conclui-se que o uso responsável de aprendizado de máquina em educação pode apoiar intervenções mais precoces, desde que respeite critérios de validade temporal, proteção de dados, interpretabilidade e utilidade pedagógica.

**Palavras-chave:** mineração de dados educacionais; previsão de desempenho escolar; aprendizado de máquina; risco pedagógico; learning analytics; séries temporais tabulares.

---

## ABSTRACT

This undergraduate thesis presents the development of a predictive system for school environments, focused on anticipating academic difficulties and supporting decision-making by teachers, pedagogical coordinators, and administrative staff. The central research problem investigates whether historical school data, such as grades, absences, payments, and academic records, can be integrated into an analytical pipeline capable of predicting a student's next grade and identifying pedagogical risk signals before failure or severe performance decline occurs. The project initially explored a graph-based approach, motivated by the relational nature of school data, but progressively evolved into a tabular temporal strategy after several analyses indicated stronger adherence between the problem and supervised models applied to longitudinal data. The final solution was organized as a reproducible pipeline composed of database maintenance and anonymization, data extraction, multi-source integration, feature engineering, temporal validation, automatic model selection, error analysis, and operational report generation. Baseline approaches, Random Forest, and HistGradientBoosting were compared for both next-grade regression and classification of risk for grades below 6.0. Results showed that, for numeric next-grade prediction, the best setting used a minimum history of one prior observation per subject, achieving MAE of 0.7601 and outperforming a simple last-grade baseline. For risk alerting, the best setting used a minimum history of two prior observations, achieving F1 of 0.7437 with recall of 0.8618 in temporal testing. In addition to predictive modeling, a school reporting layer was developed with specific outputs for teachers, coordination, and school administration, including an executive ranking of priority students. The main contribution of this work is to demonstrate that a temporal analytical architecture oriented toward institutional use, combined with interpretation and prioritization mechanisms, is more suitable for school contexts than isolated classification approaches or purely relational exploration. It is concluded that the responsible use of machine learning in education can support earlier intervention, provided that temporal validity, data protection, interpretability, and pedagogical usefulness are respected.

**Keywords:** educational data mining; student performance prediction; machine learning; pedagogical risk; learning analytics; tabular temporal modeling.

---

## LISTA DE SIGLAS E ABREVIATURAS

- ABNT: Associação Brasileira de Normas Técnicas
- API: Application Programming Interface
- CSV: Comma-Separated Values
- EDM: Educational Data Mining
- F1: F1-Score
- INEP: Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira
- LA: Learning Analytics
- LDB: Lei de Diretrizes e Bases da Educação Nacional
- LGPD: Lei Geral de Proteção de Dados Pessoais
- LSTM: Long Short-Term Memory
- MAE: Mean Absolute Error
- ML: Machine Learning
- PCA: Principal Component Analysis
- RMSE: Root Mean Squared Error
- SQL: Structured Query Language
- TCC: Trabalho de Conclusão de Curso
- XAI: Explainable Artificial Intelligence

---

## SUMÁRIO

1. Introdução  
2. Problema de pesquisa  
3. Objetivos  
4. Justificativa  
5. Fundamentação teórica  
6. Trabalhos relacionados  
7. Materiais e métodos  
8. Evolução histórica do projeto  
9. Arquitetura proposta  
10. Tratamento e integração dos dados  
11. Modelagem preditiva  
12. Geração de relatórios escolares  
13. Resultados experimentais  
14. Discussão dos resultados  
15. Limitações do trabalho  
16. Conclusão  
17. Trabalhos futuros  
18. Referências  
19. Apêndices

---

# 1. INTRODUÇÃO

O contexto educacional contemporâneo é marcado por um volume crescente de dados administrativos, acadêmicos e operacionais produzidos diariamente pelas escolas. Matrículas, notas, faltas, registros financeiros, dados cadastrais, informações de turma e histórico escolar formam um ecossistema informacional que, em muitos casos, permanece subutilizado no momento de apoiar decisões pedagógicas. Embora escolas e sistemas educacionais registrem continuamente esses dados, a capacidade institucional de transformá-los em conhecimento acionável ainda é limitada em grande parte das realidades escolares.

No cotidiano da escola, grande parte das intervenções ocorre de forma reativa. Em geral, o professor, a coordenação ou a secretaria conseguem perceber o problema quando a dificuldade do aluno já se tornou evidente em notas muito baixas, aumento significativo de faltas, queda prolongada de rendimento ou risco concreto de reprovação. Nesse estágio, a margem de ação pedagógica é menor, o custo institucional é maior e a chance de reversão do quadro pode ser reduzida.

Nesse cenário, surgem duas questões centrais. A primeira é se os dados já disponíveis nas escolas podem ser utilizados para antecipar sinais de risco acadêmico. A segunda é se essa antecipação pode ser transformada em relatórios compreensíveis e úteis para diferentes perfis institucionais, como professores, coordenação pedagógica e secretaria. Este trabalho responde a essas questões por meio da construção de uma pipeline de análise preditiva aplicada a dados escolares reais.

A proposta deste TCC não se limita a prever aprovação ou reprovação. O foco é mais específico e operacional: prever a próxima nota do aluno e, simultaneamente, classificar o risco de que essa nota entre em uma faixa pedagogicamente crítica. A partir dessa dupla finalidade, o sistema busca produzir alertas mais precoces e mais úteis, permitindo ações diferenciadas conforme o tipo de usuário escolar. Para o professor, o valor está em perceber a tempo quais alunos e disciplinas exigem ajuste de abordagem. Para a coordenação, o ganho está em priorizar casos e grupos críticos. Para a secretaria, o objetivo é cruzar sinais acadêmicos com elementos administrativos que possam exigir contato preventivo com a família.

Do ponto de vista científico, o trabalho se insere na interseção entre Mineração de Dados Educacionais e Learning Analytics. Essas áreas defendem que dados educacionais podem apoiar compreensão, monitoramento e melhoria dos processos de aprendizagem. Entretanto, o uso desses dados não deve ser feito de maneira puramente técnica. Em educação, qualquer modelo preditivo precisa respeitar o caráter sensível do contexto, a necessidade de interpretabilidade e o compromisso de que a decisão final continue humana, contextualizada e pedagógica.

O projeto teve início com uma hipótese estruturalmente diferente da solução final. Inicialmente, o domínio escolar foi interpretado como um sistema relacional complexo, passível de representação por grafos. Essa fase buscou modelar relações entre alunos, matrículas, notas, faltas, pagamentos e responsáveis. Posteriormente, o projeto passou por experimentos com classificadores tradicionais, PCA, grafos heterogêneos, consultas em NetworkX, estrutura para PyTorch e uma etapa exploratória com LSTM. Apesar da relevância dessas fases, a experiência empírica indicou que o problema principal apresentava melhor aderência a uma modelagem tabular temporal.

O resultado desse percurso foi a refatoração do projeto para uma arquitetura única e reprodutível, baseada em integração de dados escolares, construção de atributos temporais, validação temporal rigorosa, seleção de modelos e geração de relatórios operacionais. Em vez de permanecer em um conjunto disperso de experimentos, o sistema foi reorganizado em uma pipeline real de dados e modelagem.

Este TCC, portanto, apresenta não apenas um modelo de aprendizado de máquina, mas a trajetória completa de um projeto que amadureceu metodologicamente até chegar a uma solução mais adequada ao problema real. Esse amadurecimento é parte essencial da contribuição acadêmica do trabalho, pois mostra como a escolha de um modelo ou de uma arquitetura precisa estar subordinada à natureza dos dados, ao contexto de uso e ao objetivo institucional do sistema.

## 1.1 Delimitação do tema

Embora o domínio da analítica educacional seja amplo, este trabalho delimita seu escopo de forma bastante objetiva. A pesquisa não trata de evasão escolar em sentido amplo, não modela desempenho em avaliações externas padronizadas e não pretende substituir critérios formais de avaliação escolar. O foco está em uma realidade mais imediata e operacional: o acompanhamento contínuo do desempenho do aluno dentro da escola a partir dos registros já existentes no sistema institucional.

Também não se trata de um estudo sociológico completo sobre causas profundas do fracasso escolar. As variáveis utilizadas refletem o que estava disponível na base acadêmica e administrativa analisada. Assim, o trabalho se concentra na construção de um mecanismo de apoio à decisão que usa indícios quantitativos para priorizar atenção pedagógica.

Em termos temporais, o TCC também é delimitado por dados históricos já encerrados o suficiente para permitir criação de alvo observável. Isso explica por que a base atualizada até 2026 nem sempre entra integralmente como ano de teste para todos os cenários: para prever a "próxima nota", é necessário que essa próxima observação exista de fato no histórico.

## 1.2 Hipóteses do trabalho

O trabalho foi desenvolvido com base em quatro hipóteses centrais:

1. Existe sinal preditivo útil em variáveis escolares rotineiramente registradas, especialmente notas, faltas e informações financeiras.
2. A representação temporal tabular dos dados escolares é mais aderente ao problema de previsão da próxima nota do que a representação puramente relacional em forma de grafo, ao menos no contexto desta base.
3. A combinação de previsão numérica com classificação de risco oferece mais valor institucional do que qualquer uma das duas saídas isoladamente.
4. A utilidade real do sistema depende não apenas do desempenho estatístico, mas da sua capacidade de gerar relatórios compreensíveis e acionáveis.

Essas hipóteses foram sendo testadas ao longo da evolução do projeto e, ao final, receberam confirmação parcial ou integral a partir dos resultados obtidos.

## 1.3 Estrutura do trabalho

Este TCC foi organizado de forma a refletir tanto a construção conceitual quanto a evolução prática do projeto. Os primeiros capítulos apresentam o problema, os objetivos, a justificativa e a fundamentação teórica. Em seguida, o texto descreve os trabalhos relacionados e a metodologia empregada. Posteriormente, detalha-se a evolução histórica do projeto, a arquitetura final da solução, o tratamento dos dados, a modelagem preditiva e a camada de relatórios. Na sequência, são apresentados os resultados experimentais, a discussão crítica, as limitações e as conclusões. Ao final, incluem-se referências e apêndices com apoio à leitura técnica.

---

# 2. PROBLEMA DE PESQUISA

O problema central deste trabalho pode ser formulado da seguinte maneira:

**Como integrar dados escolares históricos de notas, faltas, pagamentos e registros acadêmicos em uma pipeline preditiva capaz de antecipar a próxima nota do aluno e sinalizar risco pedagógico, produzindo relatórios úteis para a tomada de decisão institucional?**

A partir desse problema central, derivam-se os seguintes subproblemas:

1. Qual representação dos dados é mais adequada ao contexto escolar: grafo, sequência ou base tabular temporal?
2. Quais fontes de dados têm maior relevância prática para previsão de desempenho futuro?
3. Como estruturar uma validação temporal que reflita o uso real da solução no ambiente escolar?
4. Como equilibrar precisão preditiva e interpretabilidade em um contexto sensível como a educação básica?
5. Como transformar saídas técnicas de modelos preditivos em relatórios operacionais para diferentes usuários escolares?

---

# 3. OBJETIVOS

## 3.1 Objetivo geral

Desenvolver uma pipeline preditiva baseada em dados escolares reais para prever a próxima nota do aluno, identificar risco pedagógico e gerar relatórios operacionais de apoio à decisão para professores, coordenação e secretaria.

## 3.2 Objetivos específicos

1. Investigar a viabilidade de diferentes abordagens computacionais para o domínio escolar, incluindo grafos, LSTM e modelos tabulares supervisionados.
2. Realizar manutenção, limpeza e anonimização da base de dados escolar utilizada no projeto.
3. Integrar dados de notas, faltas, pagamentos e variáveis acadêmicas em uma única base longitudinal de modelagem.
4. Construir atributos temporais e contextuais relevantes para previsão da próxima nota.
5. Comparar modelos e baselines sob validação temporal.
6. Estruturar dois modos complementares de uso: previsão numérica da próxima nota e alerta de risco pedagógico.
7. Gerar relatórios específicos para professor, coordenação pedagógica e secretaria.
8. Construir um ranking executivo de alunos prioritários para ação institucional.

---

# 4. JUSTIFICATIVA

Este trabalho se justifica em três planos complementares: acadêmico, tecnológico e social.

No plano acadêmico, o projeto investiga um problema relevante da Mineração de Dados Educacionais: a previsão de desempenho escolar a partir de múltiplas fontes de dados institucionais. Ao mesmo tempo, o trabalho contribui metodologicamente ao documentar a migração de uma hipótese relacional baseada em grafos para uma arquitetura tabular temporal mais adequada ao problema, oferecendo um estudo aplicado sobre escolha de modelagem em contexto real.

No plano tecnológico, a justificativa reside na construção de uma pipeline reproduzível e orientada ao uso. Em muitos projetos acadêmicos, modelos preditivos são avaliados apenas por métricas internas, sem preocupação com integração de dados, manutenção da base, anonimização, temporalidade, geração de artefatos e relatórios operacionais. Este trabalho busca preencher essa lacuna ao entregar uma solução mais próxima de um sistema institucional do que de um experimento isolado.

No plano social e educacional, a justificativa é ainda mais forte. A escola precisa identificar precocemente sinais de dificuldade para atuar antes que o problema se torne irreversível. Quando a intervenção ocorre cedo, aumentam as possibilidades de reforço pedagógico, ajuste de abordagem, contato com a família e encaminhamento institucional adequado. Além disso, o uso de dados pode auxiliar a escola a distribuir melhor sua atenção, priorizando casos mais urgentes sem depender apenas de percepção subjetiva.

Também há justificativa ética para o trabalho. Ao contrário de abordagens que tratam previsão educacional como automação de julgamento, este TCC adota a visão de que modelos devem apoiar, e não substituir, o trabalho pedagógico humano. Dessa forma, o sistema foi pensado para produzir indícios e priorizações, e não decisões finais. Esse ponto é central em contextos educacionais e está alinhado às discussões sobre ética, privacidade e transparência em Learning Analytics.

---

# 5. FUNDAMENTAÇÃO TEÓRICA

## 5.1 Mineração de Dados Educacionais e Learning Analytics

A Mineração de Dados Educacionais é uma área dedicada ao desenvolvimento de métodos para explorar dados oriundos de contextos educacionais, buscando responder perguntas pedagógicas, administrativas e institucionais com suporte computacional. Segundo Romero e Ventura, a área se caracteriza por integrar métodos de mineração de dados, aprendizado de máquina e análise estatística para compreender fenômenos educacionais a partir de bases complexas e heterogêneas.

Learning Analytics, por sua vez, enfatiza a medição, coleta, análise e relato de dados sobre aprendizes e seus contextos, com o objetivo de compreender e otimizar a aprendizagem e os ambientes em que ela ocorre. Siemens e Baker argumentam que Educational Data Mining e Learning Analytics se desenvolveram com enfoques parcialmente distintos, mas complementares, e que a aproximação entre essas áreas é benéfica para o avanço da pesquisa aplicada em educação.

No presente trabalho, essas duas perspectivas aparecem de forma integrada. O uso de modelos supervisionados e engenharia de atributos aproxima o projeto da tradição de Mineração de Dados Educacionais. Já a geração de relatórios para ação institucional aproxima a proposta da tradição de Learning Analytics, pois o foco não está apenas em modelar, mas em produzir informação útil para intervenção pedagógica.

## 5.2 Previsão de desempenho escolar

Prever desempenho escolar é um problema clássico em educação orientada a dados. De maneira geral, esse problema pode assumir diferentes formas:

- prever nota futura;
- prever reprovação;
- prever evasão;
- prever engajamento insuficiente;
- prever necessidade de suporte adicional.

Entre essas possibilidades, a previsão da próxima nota apresenta vantagens práticas importantes. Primeiro, porque preserva a granularidade do processo de aprendizagem, captando oscilações antes que a situação do aluno se consolide como reprovação. Segundo, porque permite construir alertas pedagógicos com base em trajetória e não apenas em resultado final. Terceiro, porque produz uma métrica que pode ser comparada diretamente com o histórico do próprio estudante.

Ao mesmo tempo, a simples previsão numérica da nota não é suficiente para a escola. O valor institucional aparece quando essa nota prevista é convertida em um sinal acionável, por exemplo, o risco de entrar abaixo de uma linha crítica, como 6,0. Por isso, neste trabalho a regressão da próxima nota e a classificação de risco foram tratadas como objetivos complementares.

## 5.3 Modelos de aprendizado de máquina aplicados ao problema

### 5.3.1 Random Forest

Random Forest, proposto por Leo Breiman, é um método de ensemble baseado em múltiplas árvores de decisão geradas a partir de amostras aleatórias dos dados e subconjuntos aleatórios de atributos. Sua principal vantagem é combinar robustez, flexibilidade e bom desempenho em problemas tabulares, além de lidar relativamente bem com relações não lineares e interações entre variáveis.

No contexto deste projeto, o Random Forest foi importante por dois motivos. Primeiro, porque representou a transição do projeto de uma fase mais exploratória para uma fase mais pragmática de modelagem tabular. Segundo, porque serviu como baseline mais estruturado em comparação a regras simples baseadas apenas na última nota.

### 5.3.2 LSTM

As redes LSTM, introduzidas por Hochreiter e Schmidhuber, foram desenvolvidas para lidar com dependências de longo prazo em sequências. Em tese, o domínio escolar possui natureza temporal e, portanto, parece adequado a esse tipo de modelagem. Contudo, o sucesso de LSTM depende de uma estrutura sequencial suficientemente estável, volumosa e coerente. Em bases escolares heterogêneas, com alunos entrando e saindo, disciplinas distintas e calendários irregulares, a construção dessa sequência pode se tornar mais difícil do que a princípio parece.

No projeto, a fase com LSTM foi relevante como exploração conceitual, mas não se consolidou como solução principal, sobretudo porque a natureza do dado disponível favoreceu mais uma abordagem tabular temporal com engenharia explícita de atributos.

### 5.3.3 Gradient Boosting

O método de Gradient Boosting, formalizado por Friedman, tornou-se uma das estratégias mais fortes para dados tabulares. Ao construir modelos aditivos em sequência, corrigindo progressivamente erros residuais, essa família de algoritmos costuma apresentar desempenho elevado em problemas supervisionados com atributos heterogêneos e relações complexas.

Na solução final deste projeto, a implementação HistGradientBoosting mostrou melhor desempenho que Random Forest em cenários importantes, tanto para regressão quanto para classificação, especialmente na base atualizada e após a reorganização temporal da pipeline.

## 5.4 Dados temporais e validação em educação

Um aspecto crítico deste trabalho é a validação temporal. Em muitos estudos preditivos, utiliza-se divisão aleatória entre treino e teste. Em educação, esse procedimento pode gerar sobreavaliação do modelo, pois padrões muito próximos do mesmo aluno ou do mesmo período acabam aparecendo tanto no treino quanto no teste.

Neste TCC, a validação foi estruturada por anos letivos, utilizando treino em anos anteriores, validação em ano intermediário e teste no ano mais recente com alvo consolidado. Essa escolha aproxima a avaliação do cenário real em que a escola precisa prever o próximo período usando apenas o passado disponível até aquele momento.

## 5.5 Ética, privacidade e anonimização

O uso de dados educacionais exige atenção especial à privacidade, à ética e à finalidade do tratamento. Learning Analytics e EDM trazem benefícios potenciais, mas também riscos relacionados a identificação indevida, uso descontextualizado de previsões e reforço de vieses. Trabalhos como os de Slade e Prinsloo, Gasevic, Dawson e Jovanovic, e Khalil e Ebner mostram que privacidade, ética e anonimização não são obstáculos à análise, mas condições para que ela seja institucionalmente legítima.

No contexto brasileiro, a LGPD reforça a necessidade de proteção de dados pessoais, incluindo aqueles que podem identificar estudantes. Em razão disso, o projeto incorporou uma etapa explícita de anonimização da tabela de alunos durante o preparo da base, substituindo dados diretamente identificáveis por representações artificiais, preservando o valor analítico sem expor identidades reais.

## 5.6 Explicabilidade e apoio à decisão

Em aplicações educacionais, a interpretabilidade tem um papel diferente daquele observado em muitos cenários industriais. Em um sistema de recomendação de produtos, por exemplo, o usuário final pode tolerar algum grau de opacidade algorítmica se o resultado for funcional. Já na escola, um alerta preditivo sem explicação tende a gerar resistência institucional, baixa confiança e pouca utilidade pedagógica.

Nesse sentido, trabalhos sobre XAI em educação defendem que modelos preditivos devem ser acompanhados de mecanismos de interpretação, seja por importância de variáveis, seja por explicações locais, seja por traduções semânticas dos sinais de risco. O presente TCC adota essa premissa não por meio de um módulo formal de explicabilidade matemática, como SHAP ou LIME, mas por meio de uma camada de interpretação institucional. Em termos práticos, isso significa converter sinais quantitativos em frases como "tendência de queda", "faltas elevadas", "pendências financeiras recorrentes" e "nota prevista abaixo da linha de segurança".

Essa estratégia possui limitações, mas oferece uma vantagem importante: aproxima a saída técnica da linguagem de trabalho dos profissionais da escola. Para o escopo deste TCC, essa forma de interpretabilidade operacional foi considerada mais alinhada ao problema do que explicações puramente estatísticas voltadas a especialistas em machine learning.

## 5.7 Qualidade de dados em sistemas escolares

Outro ponto teórico relevante diz respeito à qualidade dos dados. Bases escolares reais não são coletadas originalmente para pesquisa, mas para operação institucional. Por isso, é comum encontrar inconsistências, lacunas, duplicidades, mudanças de nomenclatura e registros incompletos. Em modelos educacionais, esse problema é especialmente importante porque a ausência de um dado pode decorrer tanto de falha de cadastro quanto de diferença legítima de trajetória escolar.

Esse aspecto reforça duas implicações teóricas para o trabalho. A primeira é que o desempenho do modelo nunca pode ser analisado sem considerar a qualidade de entrada dos dados. A segunda é que a arquitetura de uma solução preditiva em educação precisa prever mecanismos de preparação, limpeza e filtragem antes da etapa de modelagem.

---

# 6. TRABALHOS RELACIONADOS

Os trabalhos relacionados a este TCC podem ser agrupados em três eixos principais: revisões da área, estudos preditivos aplicados à educação e discussões sobre interpretabilidade e ética.

No eixo das revisões, Romero e Ventura apresentam uma síntese ampla da Mineração de Dados Educacionais, destacando tipos de usuários, ambientes, métodos e finalidades analíticas. O Handbook of Educational Data Mining, organizado por Romero, Ventura, Pechenizkiy e Baker, reforça a consolidação da área e mostra a diversidade de problemas que podem ser tratados com técnicas computacionais em educação.

No eixo preditivo, estudos recentes sobre evasão e desempenho mostram que atributos acadêmicos, financeiros e de engajamento podem ser úteis para antecipar dificuldades. Ainda que muitos trabalhos estejam concentrados no ensino superior, suas contribuições metodológicas são relevantes para este TCC, especialmente no que diz respeito à combinação de variáveis históricas, validação temporal e uso de múltiplas fontes de dados.

No eixo da interpretabilidade, estudos de IA explicável em educação mostram que desempenho preditivo isolado não basta. Em contextos institucionais, é necessário justificar por que um caso foi priorizado, quais sinais contribuíram para a decisão e como essa informação pode apoiar o profissional humano. Por isso, este TCC não se limita a gerar predições, mas converte saídas de modelo em fatores de alerta, recomendações e rankings executivos.

## 6.1 Convergências com a literatura

Há convergência clara entre a literatura e este trabalho em pelo menos quatro pontos. Primeiro, no reconhecimento de que dados educacionais possuem forte potencial para monitorar risco e apoiar intervenção. Segundo, na necessidade de combinar múltiplas fontes de informação, em vez de depender exclusivamente de notas. Terceiro, na importância da temporalidade para evitar avaliações artificiais. Quarto, na exigência de mecanismos de explicação e governança do uso institucional.

## 6.2 Diferenças em relação a estudos clássicos

Boa parte da literatura concentra-se em ensino superior, evasão universitária ou ambientes virtuais de aprendizagem. Este TCC se diferencia ao trabalhar com uma realidade escolar mais ampla, articulando acompanhamento bimestral de desempenho, faltas e sinais administrativos. Outra diferença importante é o foco simultâneo em duas saídas complementares: previsão da próxima nota e risco pedagógico. Em vez de trabalhar apenas com um rótulo final de aprovação ou reprovação, o projeto acompanha o processo intermediário de deterioração ou recuperação do desempenho.

## 6.3 Contribuição específica do presente TCC

Em relação aos trabalhos relacionados, a principal contribuição específica deste TCC está na articulação entre:

- trajetória real de experimentação;
- refatoração arquitetural documentada;
- validação temporal;
- geração de relatórios operacionais;
- ranking executivo de prioridade.

Essa combinação não é comum em trabalhos que se limitam à comparação de algoritmos em datasets prontos. Aqui, a contribuição envolve desde a preparação da base até a forma como o resultado chega ao usuário institucional.

---

# 7. MATERIAIS E MÉTODOS

## 7.1 Natureza da pesquisa

Esta pesquisa é aplicada, de natureza quantitativa e com caráter tecnológico-experimental. É aplicada porque busca resolver um problema concreto de gestão pedagógica e acompanhamento escolar. É quantitativa porque trabalha com dados históricos estruturados, métricas preditivas e validação estatística. É tecnológica porque envolve o desenvolvimento efetivo de software, pipeline de dados, modelos de aprendizado de máquina e relatórios operacionais.

## 7.2 Estratégia metodológica

A estratégia metodológica adotada foi incremental e iterativa. Em vez de partir diretamente para uma solução final, o projeto foi conduzido em ciclos:

1. exploração do domínio e das fontes de dados;
2. experimentação com diferentes representações;
3. identificação de limitações de cada abordagem;
4. refatoração arquitetural;
5. consolidação em pipeline real;
6. avaliação temporal;
7. geração de relatórios institucionais.

Essa trajetória é importante porque revela que a solução final não foi arbitrária. Ela resultou da observação empírica de quais estruturas e modelos aderiam melhor ao problema real.

## 7.3 Ambiente computacional

O projeto foi desenvolvido em Python, com organização modular do repositório e apoio de bibliotecas de ciência de dados e aprendizado de máquina. O banco de origem foi tratado via SQL e a extração de dados foi convertida para arquivos CSV, que alimentam a pipeline final. A modelagem tabular utilizou principalmente implementações disponíveis no ecossistema scikit-learn.

## 7.4 Fonte de dados

Os dados utilizados são provenientes de uma base escolar real, contendo informações relacionadas a:

- alunos;
- médias e notas;
- faltas;
- pagamentos;
- responsáveis;
- informações acadêmicas e administrativas.

A base foi atualizada até **4 de abril de 2026**, e passou por processo de manutenção, redução estrutural, exclusão de tabelas irrelevantes, anonimização e reorganização de índices.

## 7.5 Procedimentos de preparação da base

O fluxo de preparação do banco incluiu:

1. renomeação da base para `COLEGIO_TESTE`;
2. exclusão iterativa de tabelas, gatilhos e visões não necessárias ao escopo do TCC;
3. anonimização da tabela de alunos;
4. reorganização de índices e atualização de estatísticas;
5. reextração dos arquivos CSV.

Esse procedimento teve dupla finalidade: reduzir peso operacional da base e aumentar a segurança no uso acadêmico dos dados.

## 7.6 Fases metodológicas detalhadas

Para fins de clareza, a pesquisa pode ser descrita em cinco grandes fases metodológicas:

**Fase 1 - Diagnóstico do domínio e exploração inicial**  
Nesta etapa, o objetivo foi compreender a estrutura dos dados escolares e mapear quais tabelas, entidades e relacionamentos estavam disponíveis. A partir daí, foram realizados experimentos iniciais com grafos, correlação e classificadores tradicionais.

**Fase 2 - Formulação de alternativas de modelagem**  
Com base na exploração inicial, o projeto testou abordagens diferentes, incluindo estrutura relacional em grafo, LSTM e Random Forest. Essa fase foi importante para identificar vantagens e limitações de cada estratégia.

**Fase 3 - Refatoração arquitetural**  
Após a constatação de que a base pivotada e a estrutura experimental não eram suficientes para o objetivo institucional do TCC, foi implementada uma nova arquitetura modular no diretório `TCCPipeline`.

**Fase 4 - Consolidação dos experimentos principais**  
Nessa fase foram definidos: fonte de dados final, modos de execução, conjuntos de atributos, critérios de seleção, validação temporal e relatórios técnicos.

**Fase 5 - Conversão dos resultados em inteligência operacional**  
Por fim, o trabalho passou a incorporar relatórios específicos para cada ator escolar e um ranking executivo de alunos prioritários.

## 7.7 Critérios de avaliação do sistema

Os critérios de avaliação do sistema foram definidos em duas camadas. A primeira camada é estatística, composta por MAE, RMSE, precision, recall e F1. A segunda camada é institucional, composta por perguntas como:

- o sistema consegue priorizar casos mais urgentes?
- a informação gerada é compreensível por profissionais da escola?
- os relatórios permitem diferenciação de ação conforme o papel institucional?
- a predição chega em tempo hábil para apoiar intervenção?

Essa dupla camada foi necessária porque um modelo educacional pode apresentar bom desempenho matemático e, ainda assim, ser pouco útil para o usuário real.

## 7.8 Considerações éticas da pesquisa

Do ponto de vista ético, o projeto partiu do princípio de minimização de exposição de dados pessoais. A manutenção do banco incluiu anonimização dos registros de alunos e a saída final dos relatórios foi estruturada para fins acadêmicos e de demonstração funcional, sem divulgar nomes reais. Além disso, o sistema foi concebido como ferramenta de apoio, não de julgamento automático. Em nenhuma etapa o modelo é proposto como substituto de avaliação humana.

---

# 8. EVOLUÇÃO HISTÓRICA DO PROJETO

## 8.1 Fase inicial orientada a grafo

O projeto começou a partir da hipótese de que o domínio escolar poderia ser representado como um grafo heterogêneo. Nessa etapa, foram produzidos módulos de leitura, construção e consulta do grafo, além de artefatos para uso em NetworkX e estruturas preparadas para PyTorch.

Essa escolha inicial fazia sentido porque a escola envolve relações entre múltiplas entidades: aluno, matrícula, disciplina, responsável, pagamento, ausência e resultado. Entretanto, embora conceitualmente interessante, essa estrutura se mostrou menos eficiente para o objetivo operacional de prever próxima nota e gerar alerta em tempo hábil.

## 8.2 Fase exploratória com testes clássicos e PCA

Na sequência, o projeto incorporou análises de correlação, comparação de classificadores tradicionais e testes com PCA. Essa etapa serviu para entender comportamento dos atributos e explorar sinais estatísticos de diferenciação entre alunos.

## 8.3 Fase de exploração temporal com LSTM

O uso de LSTM representou uma tentativa de tratar o histórico do aluno como sequência de eventos. Apesar do mérito conceitual, a heterogeneidade do conjunto de dados e a necessidade de uma estrutura institucionalmente interpretável dificultaram a consolidação dessa abordagem como solução principal.

## 8.4 Fase tabular com Random Forest

Posteriormente, o projeto passou a adotar uma estratégia tabular com Random Forest, transformando parte do histórico em base estruturada de treino. Essa etapa foi um avanço importante, mas ainda apresentava limitações, como pivotamento excessivo da base, perda de temporalidade e uso incompleto de faltas e pagamentos.

## 8.5 Refatoração para pipeline real

O amadurecimento do projeto culminou na criação de uma nova arquitetura no diretório `TCCPipeline`, composta por módulos de:

- configuração;
- leitura das fontes;
- engenharia de atributos;
- modelagem;
- comparação de históricos mínimos;
- relatórios.

Essa refatoração representou o ponto de consolidação do TCC, transformando uma sequência de experimentos em uma pipeline reproduzível de ponta a ponta.

## 8.6 Aprendizados metodológicos dessa evolução

O percurso histórico do projeto oferece um aprendizado metodológico importante para pesquisas aplicadas em computação: uma solução tecnicamente elegante nem sempre é a mais adequada para o problema real. A fase de grafos foi conceitualmente rica. A fase com LSTM parecia promissora pela temporalidade do domínio. A fase com Random Forest trouxe pragmatismo. No entanto, apenas a combinação entre refatoração de dados, validação temporal e relatórios institucionais tornou a solução realmente alinhada ao objetivo do TCC.

Em outras palavras, o trabalho mostra que a maturidade de um projeto aplicado não depende apenas do algoritmo escolhido, mas da coerência entre problema, dado, arquitetura e contexto de uso.

---

# 9. ARQUITETURA PROPOSTA

## 9.1 Visão geral

A arquitetura final foi organizada para separar claramente responsabilidades:

- `BDBasic/DataExtraction/DatabaseMaintenance.py`: manutenção, anonimização e otimização da base;
- `BDBasic/DataExtraction/Treatment.py`: reextração dos CSVs;
- `TCCPipeline/data.py`: leitura e preparo inicial das fontes;
- `TCCPipeline/dataset.py`: construção do dataset longitudinal e engenharia de atributos;
- `TCCPipeline/modeling.py`: validação temporal, seleção de candidatos, treinamento e avaliação;
- `TCCPipeline/reporting.py`: geração dos relatórios operacionais;
- `TCCPipeline/pipeline.py`: orquestração da execução.

## 9.2 Modos de execução

A pipeline foi dividida em dois modos:

1. `previsao_nota`: focado em regressão da próxima nota, com histórico mínimo de 1;
2. `alerta_risco`: focado em classificação de risco de próxima nota abaixo de 6, com histórico mínimo de 2.

Essa divisão foi necessária porque os experimentos mostraram que o melhor corte de histórico não era o mesmo para os dois objetivos.

## 9.3 Camada de relatórios

Além da modelagem, foi criada uma camada específica de relatórios com quatro saídas principais:

- relatório para professores;
- relatório para coordenação;
- relatório para secretaria;
- ranking executivo para coordenação.

Essa camada aproxima o sistema do uso institucional e constitui uma das principais contribuições práticas do trabalho.

## 9.4 Fluxo operacional da arquitetura

O fluxo operacional da solução pode ser descrito em oito etapas:

1. manutenção e anonimização da base original;
2. extração das tabelas relevantes para CSV;
3. leitura estruturada dos arquivos pela pipeline;
4. construção do dataset longitudinal;
5. separação temporal de treino, validação e teste;
6. comparação e seleção automática de candidatos;
7. geração de predições e análises de erro;
8. produção de relatórios operacionais para usuários da escola.

Essa decomposição torna a solução mais defensável academicamente, pois deixa claro que o trabalho não consiste apenas em "rodar um algoritmo", mas em estruturar todo o ciclo analítico.

## 9.5 Decisões de engenharia relevantes

Algumas decisões de engenharia foram particularmente importantes para a arquitetura final:

- preservar o histórico do projeto sem apagar as fases anteriores;
- manter a execução principal simples no `main.py`;
- separar modos de uso por objetivo analítico;
- salvar artefatos e relatórios em diretórios específicos por modo;
- registrar todas as etapas de refatoração em arquivo próprio de acompanhamento;
- introduzir um arquivo `AGENTS.md` para garantir rastreabilidade de futuras alterações.

Essas decisões favorecem manutenção, apresentação acadêmica e continuidade futura do projeto.

---

# 10. TRATAMENTO E INTEGRAÇÃO DOS DADOS

## 10.1 Dados extraídos

Os principais arquivos extraídos e utilizados no trabalho foram:

- `aluno.csv`;
- `media_nota_aluno.csv`;
- `pagamento_aluno.csv`;
- `faltas_aluno.csv`;
- `responsaveis_aluno.csv`.

Além disso, o projeto passou a incorporar estrutura para `professor_disciplina.csv`, embora a base atual analisada ainda não tenha preservado esse vínculo na primeira rodada de limpeza, o que gerou a condição temporária de "Professor não identificado" nos relatórios.

## 10.2 Engenharia de atributos

Foram criados atributos como:

- nota anterior 1, 2 e 3;
- média das últimas notas;
- desvio histórico da disciplina;
- tendência da última nota;
- média histórica do aluno no ano;
- média do aluno no ano anterior;
- média da disciplina no ano anterior;
- média da coorte por etapa;
- faltas da etapa;
- faltas acumuladas;
- pagamentos registrados no ano;
- pagamentos pendentes no ano;
- média de dias até pagamento;
- presença de histórico prévio.

Esses atributos foram construídos de modo a representar apenas o histórico disponível até o ponto da previsão, preservando a causalidade temporal.

## 10.3 Construção do alvo

Foram definidos dois alvos:

1. `target_nota_proxima`: valor numérico da próxima nota observada;
2. `target_risco_proxima`: indicador binário de risco, assumindo 1 quando a próxima nota observada é inferior a 6,0.

Essa escolha permitiu separar utilidade numérica e utilidade institucional.

## 10.4 Tratamento de ausências e dados faltantes

Em bases escolares reais, a ausência de um valor não deve ser interpretada de maneira simplista. Um aluno pode não ter registro de falta em uma etapa por realmente não ter faltado, por não haver lançamento naquele período ou por sua trajetória naquele componente não seguir exatamente o padrão da maioria dos casos. O mesmo vale para pagamentos, médias parciais e vínculos disciplinares.

Por esse motivo, a pipeline tratou dados faltantes de forma controlada, preenchendo somente quando havia justificativa semântica clara, como no caso de faltas inexistentes em determinada etapa. Em outras situações, os valores foram preservados como ausentes e tratados pelos mecanismos internos do pipeline de modelagem, evitando imputações arbitrárias que pudessem introduzir viés.

## 10.5 Prevenção de vazamento de informação

Um cuidado central da construção do dataset foi evitar vazamento de informação futura. Em problemas temporais, esse risco ocorre quando atributos calculados usam, direta ou indiretamente, observações posteriores ao momento da previsão. Para evitar isso, todos os atributos históricos foram calculados a partir de deslocamentos, médias acumuladas, resumos anteriores e agregações limitadas ao passado conhecido. O próprio alvo da próxima nota só foi construído após a organização temporal da sequência por aluno, período e disciplina.

Esse ponto é particularmente importante para a validade do trabalho, pois uma solução aparentemente precisa, mas alimentada por informação do futuro, teria pouca utilidade em ambiente real.

---

# 11. MODELAGEM PREDITIVA

## 11.1 Modelos candidatos

Os modelos candidatos incluídos na pipeline foram:

- Random Forest Regressor;
- Random Forest Classifier;
- HistGradientBoostingRegressor;
- HistGradientBoostingClassifier.

Também foram comparados baselines determinísticos:

- última nota;
- média das duas últimas notas;
- média das três últimas notas;
- baseline híbrido.

## 11.2 Critérios de seleção

A seleção foi realizada no conjunto de validação temporal, respeitando o seguinte:

- para regressão, o critério principal foi menor MAE;
- para classificação, o critério principal foi maior F1.

## 11.3 Métricas utilizadas

Para regressão:

- MAE;
- RMSE;
- proporção de acerto com erro absoluto menor ou igual a 0,5.

Para classificação:

- precision;
- recall;
- F1-score.

As métricas foram escolhidas porque refletem tanto proximidade numérica quanto utilidade prática para detecção de alunos em risco.

## 11.4 Justificativa para a solução final adotada

Embora redes neurais e abordagens mais sofisticadas sejam frequentemente associadas a melhor desempenho, a solução final adotada neste trabalho foi orientada por evidência empírica e adequação ao contexto. Os modelos tabulares escolhidos apresentaram cinco vantagens principais:

1. melhor aderência à forma como os dados estavam organizados;
2. facilidade de incorporar atributos construídos manualmente;
3. menor custo de treinamento e ajuste;
4. melhor capacidade de comparação com baselines simples;
5. maior facilidade de interpretação institucional.

Isso não significa que abordagens profundas devam ser descartadas em investigações futuras. Significa apenas que, para o problema e a base atuais, a melhor solução disponível foi uma arquitetura tabular temporal.

## 11.5 Por que manter baselines simples no pipeline

A manutenção explícita de baselines dentro da pipeline final foi uma decisão metodológica deliberada. Muitas vezes, projetos acadêmicos descrevem baselines apenas no texto e não os mantêm como candidatos reais do sistema. Neste trabalho, os baselines continuam ativos na seleção, de modo que o modelo mais complexo só é escolhido quando supera de fato as soluções simples.

Essa decisão fortalece a honestidade experimental do TCC e ajuda a evitar conclusões artificiais de superioridade algorítmica.

---

# 12. GERAÇÃO DE RELATÓRIOS ESCOLARES

## 12.1 Relatório do professor

O relatório do professor organiza casos por disciplina e etapa, destacando:

- nota atual;
- nota prevista;
- pontuação de risco;
- tendência;
- faltas acumuladas;
- fatores de alerta;
- recomendação pedagógica sugerida.

As recomendações foram calibradas por perfil de disciplina, diferenciando áreas como linguagens, humanas e exatas.

## 12.2 Relatório da coordenação

O relatório da coordenação resume:

- agrupamentos críticos por série e disciplina;
- quantidade de alunos monitorados;
- casos de alto risco;
- taxa de alto risco;
- recomendação de encaminhamento pedagógico.

## 12.3 Relatório da secretaria

O relatório da secretaria enfatiza:

- faltas elevadas;
- pendências financeiras;
- quantidade de disciplinas monitoradas;
- prioridade administrativa;
- ação administrativa sugerida.

## 12.4 Ranking executivo

O ranking executivo consolida múltiplos sinais por aluno e período, criando:

- índice de prioridade;
- nível de prioridade executiva;
- motivos resumidos;
- ação sugerida à coordenação.

Essa saída é particularmente importante porque reduz o volume de informação e oferece uma fila objetiva de intervenção institucional.

## 12.5 Exemplo de uso institucional

Um cenário típico de uso da solução pode ser descrito da seguinte forma. No fechamento de uma etapa letiva, a escola atualiza o banco, executa a manutenção, roda a extração e em seguida executa a pipeline completa. O professor recebe uma lista dos alunos e disciplinas com maior risco de queda na próxima etapa. A coordenação recebe uma visão agregada por série e disciplina, além do ranking executivo dos alunos mais urgentes. A secretaria identifica quais casos têm também sinais administrativos, como frequência ou financeiro, e pode realizar contato preventivo com a família.

Esse fluxo demonstra como a solução se encaixa em uma rotina institucional plausível, sem exigir infraestrutura complexa ou mudança radical no processo escolar.

---

# 13. RESULTADOS EXPERIMENTAIS

## 13.1 Comparação do histórico mínimo

Os testes com histórico mínimo mostraram:

- `min_history = 1`: melhor para regressão;
- `min_history = 2`: melhor para classificação de risco;
- `min_history = 3`: inviabilizou a validação temporal na rodada analisada.

Os resultados observados foram:

| Configuração | Regressão MAE | Classificação F1 | Situação |
| --- | ---: | ---: | --- |
| min_history = 1 | 0,7601 | 0,7350 | Melhor regressão |
| min_history = 2 | 0,8045 | 0,7437 | Melhor classificação |
| min_history = 3 | - | - | Erro por falta de suporte temporal |

## 13.2 Resultados do modo previsão de nota

No modo `previsao_nota`, a pipeline utilizou:

- 106.721 linhas de modelagem;
- 1.378 alunos únicos;
- 53 disciplinas;
- 6 anos letivos únicos;
- treino com 2020 a 2023;
- validação em 2024;
- teste em 2025.

O melhor modelo de regressão foi o `hist_gradient_boosting_regressor`, com:

- MAE = 0,7601;
- RMSE = 1,0434;
- acerto com erro <= 0,5 = 0,4613.

O baseline de última nota obteve MAE = 0,9138. Assim, houve melhora relevante da solução proposta sobre a heurística simples.

## 13.3 Resultados do modo alerta de risco

No modo `alerta_risco`, a pipeline utilizou:

- 50.065 linhas de modelagem;
- 1.179 alunos únicos;
- 53 disciplinas;
- 5 anos letivos únicos;
- treino com 2021 a 2023;
- validação em 2024;
- teste em 2025.

O melhor classificador foi o `hist_gradient_boosting_classifier`, com:

- precision = 0,6540;
- recall = 0,8618;
- F1 = 0,7437.

O baseline alcançou F1 = 0,7243. O ganho mais relevante esteve no recall, o que é desejável em um sistema de alerta, já que perder alunos em risco é mais grave do que sinalizar casos adicionais para monitoramento.

## 13.4 Análise de erro

A análise de erro mostrou concentração de maiores dificuldades em:

- Biologia 2;
- componentes segmentados de Matemática;
- História 2;
- Química 3;
- séries finais do fundamental e do ensino médio.

Também foi observado que faixas de nota abaixo de 7 apresentam maior erro médio, o que confirma a dificuldade estrutural de prever com precisão justamente os casos mais instáveis e mais relevantes para a intervenção pedagógica.

## 13.5 Calibração da régua de risco

Inicialmente, a regra de risco gerava excesso de casos classificados como alto risco. Para resolver isso, foi criada uma pontuação composta de risco, combinando:

- predição de risco do modelo;
- nota prevista;
- nota atual;
- variação esperada;
- faltas acumuladas;
- pendências financeiras.

Após a calibração:

- alto risco passou de 7.838 casos para 4.070;
- moderado passou de 5.156 para 2.440;
- a priorização ficou mais compatível com uso institucional.

## 13.6 Ranking executivo

O ranking executivo gerou uma fila consolidada de priorização por aluno. Na rodada atual, houve forte concentração de casos em prioridade crítica e alta, o que indica que ainda existe espaço para futura recalibração dos limiares. Ainda assim, o ranking cumpriu seu papel de destacar, de forma objetiva, alunos com combinação severa de:

- muitas disciplinas em alto risco;
- pontuação máxima elevada;
- média prevista abaixo da linha de segurança;
- faltas críticas;
- pendências financeiras recorrentes.

## 13.7 Síntese quantitativa da camada operacional

Após a calibração da régua de risco, a camada integrada de relatórios passou a apresentar, para o período testado de 2025:

- 26.527 registros disciplinares avaliados;
- 20.017 casos classificados como baixo risco;
- 2.440 casos classificados como risco moderado;
- 4.070 casos classificados como alto risco.

Além disso, o ranking executivo consolidou 623 registros por aluno e período, distribuídos em:

- 498 casos em prioridade crítica;
- 125 casos em prioridade alta.

Esse resultado mostra que a camada operacional já é capaz de reduzir dezenas de milhares de registros disciplinares a uma lista executiva de algumas centenas de alunos prioritários, o que representa ganho importante de foco institucional.

## 13.8 Interpretação dos resultados sob a ótica escolar

Para a escola, um MAE de 0,7601 não deve ser lido apenas como indicador matemático. Em termos práticos, significa que, em média, a previsão da próxima nota ficou a menos de um ponto da nota realmente observada, o que é suficientemente relevante para antecipar boa parte dos casos mais delicados. Da mesma forma, um recall de 0,8618 para risco significa que o sistema foi capaz de recuperar grande parte dos alunos que de fato entraram em zona crítica na nota seguinte.

Em contexto educacional, esses números não eliminam a necessidade de análise humana, mas justificam o uso do sistema como mecanismo de triagem e priorização.

---

# 14. DISCUSSÃO DOS RESULTADOS

Os resultados obtidos permitem discutir o trabalho em quatro dimensões: aderência do modelo ao problema, relevância da arquitetura, utilidade institucional e limites interpretativos.

## 14.1 Aderência do modelo ao problema

O primeiro ponto importante é que a solução final mostra aderência melhor ao problema do que as hipóteses iniciais. O projeto começou explorando grafos e depois LSTM, mas a experimentação revelou que o problema real era mais bem representado por uma base tabular temporal com engenharia explícita de atributos. Isso não significa que grafos ou redes recorrentes sejam tecnicamente inadequados em qualquer cenário educacional. Significa, especificamente, que no conjunto de dados e no escopo institucional analisados, a melhor relação entre viabilidade, desempenho e interpretabilidade foi obtida com modelos tabulares.

## 14.2 Importância da validação temporal

Outro ponto central é a importância da validação temporal. O uso de treino em anos anteriores, validação em 2024 e teste em 2025 fortalece a credibilidade dos resultados, pois aproxima a avaliação do uso real. Em contexto educacional, essa escolha é particularmente importante, já que mudanças de coorte, série, disciplina e comportamento escolar podem distorcer resultados quando se usa apenas divisão aleatória.

## 14.3 O valor dos baselines

O trabalho também mostrou que baselines simples continuam relevantes. Em várias fases do projeto, regras como repetir a última nota ou usar médias móveis competiram fortemente com modelos mais sofisticados. Isso é um achado metodologicamente importante, porque reforça que complexidade algorítmica não deve ser assumida como sinônimo de superioridade. A adoção final de HistGradientBoosting só se justifica porque, nos cenários atuais e após a refatoração dos dados, houve ganho mensurável sobre os baselines.

## 14.4 Utilidade institucional dos relatórios

Do ponto de vista prático, o maior avanço do projeto está na passagem da predição para a ação. O valor institucional não está apenas em obter um MAE menor ou um F1 maior, mas em traduzir esses resultados em relatórios úteis. O trabalho mostra que isso é possível ao separar saídas para professor, coordenação e secretaria, respeitando o tipo de decisão de cada um.

Para o professor, a informação útil é granular e disciplinar.  
Para a coordenação, é agregada e priorizada.  
Para a secretaria, é administrativa e preventiva.

Essa separação foi decisiva para alinhar a solução ao objetivo original do TCC.

## 14.5 Questões de interpretação e cautela

Apesar dos avanços, é preciso evitar leituras deterministas do sistema. Uma predição de nota baixa ou um sinal de risco não significa que o aluno está condenado ao fracasso, nem que a causa é exclusivamente pedagógica. O modelo capta padrões históricos, mas a realidade escolar é influenciada por múltiplos fatores contextuais, familiares, emocionais, didáticos e institucionais.

Assim, a saída do sistema deve ser entendida como **sinal de atenção**, e não como juízo final sobre o aluno. Essa é uma posição metodológica e ética do trabalho.

## 14.6 A relação entre utilidade e sobrecarga institucional

Uma discussão importante diz respeito ao equilíbrio entre sensibilidade e sobrecarga institucional. Quanto mais sensível a régua de risco, maior a probabilidade de capturar alunos realmente problemáticos. No entanto, também aumenta a chance de saturar professores e coordenação com excesso de alertas. A calibração implementada na etapa final do trabalho procurou justamente reduzir esse efeito, transformando uma classificação excessivamente ampla em uma priorização mais concentrada.

Ainda assim, a forte presença de casos classificados como críticos no ranking executivo sugere que novas calibrações serão necessárias para alinhar o sistema à capacidade operacional real da escola.

## 14.7 A contribuição da documentação do processo

Outro aspecto que merece destaque é o valor da documentação contínua do projeto. O arquivo de registro criado ao longo do desenvolvimento não é apenas uma conveniência técnica. Ele se tornou parte da metodologia do TCC, permitindo reconstruir decisões, justificar mudanças e demonstrar maturidade processual. Em um trabalho que passou por diferentes hipóteses de modelagem, essa rastreabilidade foi decisiva.

---

# 15. LIMITAÇÕES DO TRABALHO

As principais limitações identificadas são:

1. O vínculo com professores ainda não está plenamente refletido na base atual analisada, devido à primeira limpeza do banco ter removido tabelas de vínculo antes da correção da rotina.
2. O ranking executivo ainda concentra muitos casos na faixa crítica, indicando necessidade futura de calibrar limiares.
3. A base de 2026 já existe no banco, mas ainda não entrou de forma robusta em todos os testes como ano-alvo, pois a construção do alvo depende de continuidade observacional.
4. O projeto utiliza dados institucionais disponíveis, mas não incorpora ainda variáveis qualitativas, socioemocionais ou contextuais registradas fora dos sistemas tradicionais.
5. A solução foi construída a partir de uma realidade escolar específica, o que exige cautela na generalização para outras instituições sem adaptação prévia.

## 15.1 Ameaças à validade interna

As ameaças à validade interna estão relacionadas principalmente à qualidade da base e à natureza observacional dos dados. Nem toda queda de desempenho decorre diretamente das variáveis disponíveis no sistema. Assim, relações capturadas pelo modelo devem ser entendidas como associações preditivas, e não como causalidade comprovada.

## 15.2 Ameaças à validade externa

A validade externa é limitada pela origem institucional dos dados. Diferentes escolas podem possuir calendários, critérios de avaliação, nomenclaturas de disciplina e padrões de registro distintos. Isso significa que a arquitetura geral pode ser reaproveitada, mas os resultados numéricos não devem ser generalizados sem adaptação e nova validação local.

## 15.3 Ameaças à validade de construção

Há também ameaças à validade de construção, pois alguns conceitos educacionais complexos, como engajamento, vulnerabilidade familiar, motivação ou clima de sala, foram representados apenas por proxies quantitativos indiretos, como faltas, pagamentos e trajetória de notas. Essa simplificação é inevitável em projetos baseados em dados institucionais, mas precisa ser reconhecida explicitamente.

---

# 16. CONCLUSÃO

Este Trabalho de Conclusão de Curso apresentou o desenvolvimento de um sistema preditivo para apoio à decisão pedagógica a partir de dados escolares reais. O projeto teve início com uma hipótese baseada em grafos, passou por experimentações com classificadores tradicionais e LSTM, e foi progressivamente refatorado até se consolidar em uma pipeline temporal tabular reproduzível.

A solução final demonstrou que:

- é viável prever a próxima nota do aluno com desempenho superior a baselines simples;
- é viável identificar risco de próxima nota abaixo de 6 com recall elevado em validação temporal;
- é viável integrar notas, faltas e pagamentos em uma arquitetura única;
- é viável transformar previsões técnicas em relatórios úteis para professor, coordenação e secretaria.

Em termos de desempenho, o modo de previsão numérica atingiu MAE de 0,7601, enquanto o modo de alerta de risco atingiu F1 de 0,7437 e recall de 0,8618 no teste temporal. Em termos institucionais, a criação da camada de relatórios e do ranking executivo aproximou o projeto do problema real da escola: agir antes que a situação do aluno se agrave.

O principal mérito do trabalho não está apenas nos números obtidos, mas na construção de uma solução coerente com o contexto educacional, tecnicamente justificável, eticamente defensável e orientada à ação institucional. Ao demonstrar que previsões podem ser convertidas em apoio concreto à prática escolar, o trabalho contribui para o debate sobre o uso responsável de aprendizado de máquina em educação.

Por fim, o trabalho reforça um princípio que deve orientar toda aplicação de IA em educação: a tecnologia deve ampliar a capacidade de cuidado institucional, e não reduzir o aluno a um rótulo. Quando usada com critério, rastreabilidade e supervisão humana, a analítica preditiva pode deixar de ser apenas uma curiosidade técnica e se tornar uma ferramenta legítima de apoio à escola.

---

# 17. TRABALHOS FUTUROS

Como continuidade do projeto, propõem-se os seguintes desdobramentos:

1. reincorporar plenamente a variável de professor após nova restauração do banco e nova extração;
2. gerar relatórios por docente e por turma;
3. recalibrar os níveis do ranking executivo;
4. estudar técnicas de explicabilidade adicionais;
5. avaliar o impacto real dos relatórios na prática escolar;
6. testar integração com painéis visuais;
7. explorar modelos adicionais, como CatBoost, LightGBM e métodos híbridos;
8. investigar inclusão de variáveis qualitativas e socioemocionais;
9. validar a solução em outras escolas ou redes.

---

# 18. REFERÊNCIAS

BAKER, R. S. J. d.; INVENTADO, P. S. Educational data mining and learning analytics. In: LARUSSON, J. A.; WHITE, B. (org.). *Learning Analytics: From Research to Practice*. New York: Springer, 2014.

BRASIL. *Lei nº 9.394, de 20 de dezembro de 1996*. Estabelece as diretrizes e bases da educação nacional. Brasília, DF: Presidência da República, 1996. Disponível em: <https://www.planalto.gov.br/ccivil_03/leis/l9394.htm>. Acesso em: 4 abr. 2026.

BRASIL. *Lei nº 13.709, de 14 de agosto de 2018*. Lei Geral de Proteção de Dados Pessoais. Brasília, DF: Presidência da República, 2018. Disponível em: <https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm>. Acesso em: 4 abr. 2026.

BREIMAN, Leo. Random forests. *Machine Learning*, v. 45, n. 1, p. 5-32, 2001. DOI: 10.1023/A:1010933404324.

FIOK, Krzysztof et al. Explainable artificial intelligence for education and training. *Human Factors in Emerging Technologies and Society*, v. 19, n. 2, 2022. DOI: 10.1177/15485129211028651.

FRIEDMAN, Jerome H. Greedy function approximation: a gradient boosting machine. *The Annals of Statistics*, v. 29, n. 5, p. 1189-1232, 2001. DOI: 10.1214/aos/1013203451.

GASEVIC, Dragan; DAWSON, Shane; JOVANOVIC, Jelena. Ethics and privacy as enablers of learning analytics. *Journal of Learning Analytics*, v. 3, n. 1, p. 1-4, 2016. DOI: 10.18608/jla.2016.31.1.

HOCHREITER, Sepp; SCHMIDHUBER, Jürgen. Long short-term memory. *Neural Computation*, v. 9, n. 8, p. 1735-1780, 1997. DOI: 10.1162/neco.1997.9.8.1735.

INEP. *Resumo Técnico: Censo Escolar da Educação Básica 2023*. Brasília, DF: Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira, 2024. Disponível em: <https://hdl.handle.net/20.500.14135/958>. Acesso em: 4 abr. 2026.

KHALIL, Mohammad; EBNER, Martin. De-identification in learning analytics. *Journal of Learning Analytics*, v. 3, n. 1, p. 129-138, 2016. DOI: 10.18608/jla.2016.31.8.

ROMERO, Cristóbal; VENTURA, Sebastián. Educational data mining: a review of the state of the art. *IEEE Transactions on Systems, Man, and Cybernetics, Part C*, v. 40, n. 6, p. 601-618, 2010. DOI: 10.1109/TSMCC.2010.2053532.

ROMERO, Cristóbal; VENTURA, Sebastián; PECHENIZKIY, Mykola; BAKER, Ryan S. J. d. (ed.). *Handbook of Educational Data Mining*. Boca Raton: CRC Press, 2010. DOI: 10.1201/b10274.

SLADE, Sharon; PRINSLOO, Paul. Learning analytics: ethical issues and dilemmas. *American Behavioral Scientist*, v. 57, n. 10, p. 1510-1529, 2013. DOI: 10.1177/0002764213479366.

SIEMENS, George; BAKER, Ryan S. J. d. Learning analytics and educational data mining: towards communication and collaboration. In: *Proceedings of the 2nd International Conference on Learning Analytics and Knowledge*. New York: ACM, 2012. p. 252-254. DOI: 10.1145/2330601.2330661.

QIANG, Ming; LIU, Ziyang; ZHANG, Ru. Explainable AI in education: integrating educational domain knowledge into the deep learning model for improved student performance prediction. *Scientific Reports*, 2026. DOI: 10.1038/s41598-026-40538-y.

---

# 19. APÊNDICES

## APÊNDICE A - ESTRUTURA DO REPOSITÓRIO

O repositório foi organizado em quatro blocos principais:

- `BDBasic`: fase histórica de exploração com grafos, testes e LSTM;
- `BDTreatment`: fase tabular inicial com Random Forest;
- `TCCPipeline`: pipeline consolidada de dados, modelagem e relatórios;
- `docs`: documentação textual do projeto e da monografia.

## APÊNDICE B - PRINCIPAIS ARQUIVOS DA PIPELINE FINAL

- `TCCPipeline/config.py`
- `TCCPipeline/data.py`
- `TCCPipeline/dataset.py`
- `TCCPipeline/modeling.py`
- `TCCPipeline/reporting.py`
- `TCCPipeline/pipeline.py`

## APÊNDICE C - PRINCIPAIS ARTEFATOS GERADOS

- `TCCPipeline/Result/previsao_nota/student_prediction_report.txt`
- `TCCPipeline/Result/alerta_risco/student_prediction_report.txt`
- `TCCPipeline/Result/relatorios_escolares/relatorio_professor.txt`
- `TCCPipeline/Result/relatorios_escolares/relatorio_coordenacao.txt`
- `TCCPipeline/Result/relatorios_escolares/relatorio_secretaria.txt`
- `TCCPipeline/Result/relatorios_escolares/ranking_executivo_coordenacao.txt`

## APÊNDICE D - OBSERVAÇÕES PARA VERSÃO FINAL ABNT

Para conversão deste rascunho em versão final conforme ABNT, recomenda-se:

1. inserir capa e folha de aprovação conforme padrão da instituição;
2. ajustar margens, fonte, espaçamento e paginação;
3. revisar citações no corpo para o formato exigido;
4. numerar corretamente seções e subseções;
5. incluir lista de figuras e tabelas, se necessário;
6. revisar referências em detalhe segundo norma adotada pela instituição.

## APÊNDICE E - DESCRIÇÃO DETALHADA DOS MÓDULOS DO SISTEMA

### E.1 Módulo de manutenção da base

O módulo de manutenção da base foi criado para atender a uma necessidade prática importante do projeto: a cada nova atualização do banco escolar, seria necessário repetir uma sequência de tarefas técnicas antes de qualquer experimento ou geração de relatório. Entre essas tarefas estavam a renomeação do banco, remoção de tabelas irrelevantes, exclusão de gatilhos e visões, anonimização de registros sensíveis e reorganização de índices.

Do ponto de vista acadêmico, esse módulo cumpre um papel relevante porque mostra que um projeto de ciência de dados em ambiente institucional não começa na etapa de modelagem. Existe uma camada anterior de engenharia e governança da base que, muitas vezes, define o sucesso ou o fracasso do trabalho.

### E.2 Módulo de extração de dados

O módulo de extração foi mantido como ponte entre o banco operacional e a pipeline analítica. Em vez de acoplar diretamente a modelagem ao banco, optou-se por gerar CSVs intermediários. Essa decisão oferece benefícios importantes:

- torna a execução reproduzível;
- facilita auditoria manual dos dados;
- permite guardar instantâneos do estado da base;
- desacopla o modelo de mudanças instantâneas do ambiente operacional;
- simplifica a apresentação acadêmica do fluxo.

### E.3 Módulo de leitura e preparação inicial

O módulo de leitura e preparação inicial da pipeline foi desenhado para padronizar formatos, nomes de colunas, tipos e representações de datas, períodos, etapas e identificadores. Sem essa etapa, os dados de notas, faltas e pagamentos permaneceriam desconectados ou difíceis de integrar.

Essa camada é uma das mais importantes do projeto porque transforma fontes brutas em tabelas semanticamente consistentes.

### E.4 Módulo de engenharia de atributos

O módulo de engenharia de atributos opera como o núcleo semântico da solução. É nele que o histórico escolar deixa de ser apenas registro bruto e se transforma em sinal analítico. A construção de notas anteriores, médias móveis, tendências, desvios, faltas acumuladas e históricos de pagamento permitiu transformar o problema em um conjunto estruturado de indícios temporais.

Em muitos projetos de aprendizado de máquina tabular, o ganho real está menos no algoritmo e mais na qualidade dos atributos. Este TCC confirma essa percepção.

### E.5 Módulo de modelagem e avaliação

O módulo de modelagem concentra:

- divisão temporal dos dados;
- seleção dos atributos efetivos;
- comparação de candidatos;
- treinamento final;
- avaliação em teste;
- geração de análise de erro.

Essa separação melhora a legibilidade do projeto e evita que regras de negócio, preparação de dados e lógica de treino fiquem misturadas em um único script.

### E.6 Módulo de relatórios

O módulo de relatórios foi desenhado para traduzir dados técnicos em linguagem institucional. Isso inclui:

- classificação de risco;
- pontuação composta;
- fatores de alerta;
- recomendações por perfil de usuário;
- ranking executivo.

Trata-se, portanto, do módulo mais alinhado ao problema final do TCC, pois é nele que a inteligência analítica é convertida em ação escolar.

## APÊNDICE F - EXEMPLO DE FLUXO DE USO NA ESCOLA

### F.1 Cenário operacional proposto

Considere uma escola que realiza fechamento parcial ao final de cada bimestre. O fluxo de uso proposto pelo sistema seria:

1. a equipe responsável atualiza a base institucional;
2. executa a rotina de manutenção e anonimização;
3. executa a extração dos CSVs;
4. roda a pipeline principal;
5. recebe os relatórios por perfil institucional;
6. realiza reunião de análise dos casos prioritários;
7. define ações pedagógicas e administrativas;
8. reavalia o efeito das ações no fechamento seguinte.

### F.2 Uso pelo professor

No caso do professor, o valor principal do sistema está na granularidade. Em vez de receber uma visão genérica da turma, ele pode identificar quais alunos, em quais disciplinas e em quais etapas apresentam maior risco. Isso permite replanejamento localizado, como:

- reforço de conteúdo específico;
- revisão de pré-requisitos;
- adaptação de estratégia de explicação;
- acompanhamento individual;
- articulação com coordenação em casos críticos.

### F.3 Uso pela coordenação pedagógica

A coordenação trabalha em nível intermediário entre caso individual e padrão institucional. Por isso, seus relatórios precisam responder a perguntas como:

- quais séries concentram mais risco?
- quais disciplinas estão mais críticas?
- quais alunos precisam de intervenção imediata?
- há padrões coletivos que indiquem necessidade de ação em turma inteira?

O ranking executivo foi pensado exatamente para esse ponto de decisão.

### F.4 Uso pela secretaria

A secretaria não atua, em geral, sobre conteúdo pedagógico, mas participa do acompanhamento da trajetória do aluno por meio de registros, frequência, comunicação com responsáveis e aspectos administrativos. Assim, a solução proposta integra esse ator institucional ao processo analítico sem transferir a ele uma responsabilidade pedagógica indevida.

## APÊNDICE G - INTERPRETAÇÃO DOS CAMPOS DOS RELATÓRIOS

### G.1 Nota atual

A nota atual representa o ponto mais recente conhecido do aluno naquela disciplina e etapa de observação. Ela serve como âncora para interpretar a previsão seguinte.

### G.2 Nota prevista

A nota prevista representa a estimativa da próxima nota observável na sequência da disciplina. Seu objetivo não é substituir a avaliação real, mas antecipar tendência de desempenho.

### G.3 Pontuação de risco

A pontuação de risco combina múltiplos fatores em uma régua única, permitindo ordenar casos mais graves antes dos menos graves. Essa pontuação é especialmente importante quando muitos alunos compartilham o mesmo nível textual de risco.

### G.4 Nível de risco

O nível de risco sintetiza a pontuação em categorias interpretáveis:

- baixo;
- moderado;
- alto.

Essa categorização facilita leitura rápida e comunicação institucional.

### G.5 Fatores de alerta

Os fatores de alerta são frases curtas que explicam os principais motivos da priorização. Seu papel é tornar o relatório menos opaco e mais útil na prática.

### G.6 Recomendação pedagógica

A recomendação pedagógica não deve ser interpretada como prescrição rígida. Ela funciona como sugestão inicial de encaminhamento, que deve ser validada e contextualizada pelo profissional da escola.

### G.7 Índice de prioridade executiva

O índice de prioridade executiva opera no nível do aluno e período, consolidando o conjunto das disciplinas. Ele permite que a coordenação decida por onde começar quando o número de casos supera a capacidade de intervenção imediata.

## APÊNDICE H - POSSÍVEIS MELHORIAS PARA A VERSÃO FINAL DO TCC

1. Inserir figuras explicando a evolução do projeto em fases.
2. Inserir diagrama da arquitetura final da pipeline.
3. Inserir tabela comparativa entre grafo, LSTM, Random Forest e HistGradientBoosting.
4. Inserir capturas dos relatórios operacionais em formato visual.
5. Inserir fluxograma da rotina de atualização do banco.
6. Incluir seção específica de requisitos não funcionais, como rastreabilidade, reprodutibilidade e segurança.
7. Produzir versão final em editor compatível com ABNT, como Word com modelo institucional ou LaTeX.

## APÊNDICE I - TEXTO SUGERIDO PARA APRESENTAÇÃO ORAL

### I.1 Abertura

Este trabalho parte de uma pergunta simples e muito prática: a escola consegue perceber cedo quais alunos estão começando a sair do caminho esperado de aprendizagem? A proposta do TCC foi justamente construir uma solução que ajudasse a responder isso com base nos dados que a escola já possui.

### I.2 Motivação

Na prática escolar, muitas intervenções acontecem tarde demais. Quando a nota final já caiu muito, a margem de recuperação é menor. Então a proposta foi prever a próxima nota e sinalizar risco antes que a situação se agrave.

### I.3 Evolução do projeto

O projeto começou com uma hipótese baseada em grafos, passou por testes com classificadores tradicionais, PCA, consultas relacionais e LSTM, até chegar a uma solução tabular temporal. Essa evolução é importante porque mostra que a solução final foi escolhida com base em aderência ao problema, e não por preferência arbitrária por um algoritmo.

### I.4 Solução final

A solução final foi uma pipeline real composta por manutenção da base, extração dos dados, engenharia de atributos, validação temporal, seleção automática de modelos e geração de relatórios para professor, coordenação e secretaria.

### I.5 Resultados

Os resultados mostraram que foi possível superar baselines simples na previsão da próxima nota e também construir um classificador de risco com recall elevado. Além disso, foi criado um ranking executivo para apoiar a coordenação na priorização dos alunos mais urgentes.

### I.6 Encerramento

Mais do que prever notas, o trabalho buscou transformar dados escolares em apoio concreto à decisão pedagógica. A principal contribuição do TCC foi mostrar que isso é tecnicamente viável, institucionalmente útil e academicamente defensável.

## APÊNDICE J - PERGUNTAS E RESPOSTAS PROVÁVEIS PARA A DEFESA

### J.1 Sobre o tema e o problema

**Qual é o tema do TCC?**  
O trabalho trata do uso de dados escolares para prever a próxima nota do aluno e identificar sinais de risco pedagógico, com o objetivo de apoiar decisões de professores, coordenação e secretaria.

**Qual é o problema central investigado?**  
O problema central é como integrar dados históricos escolares em uma pipeline capaz de antecipar desempenho futuro e transformar essa previsão em relatórios úteis para a escola.

**Por que esse problema é relevante?**  
Porque muitas intervenções escolares acontecem tarde demais. Se a escola conseguir identificar cedo sinais de queda, há mais chance de ajustar abordagem, reforço, contato com a família e acompanhamento institucional.

**O objetivo do sistema é reprovar ou rotular o aluno?**  
Não. O sistema não toma decisão final e não substitui a avaliação pedagógica. Ele produz sinais de apoio à decisão humana, com foco em prevenção e intervenção antecipada.

**Por que prever a próxima nota em vez de apenas prever reprovação?**  
Porque a próxima nota oferece um sinal mais precoce e mais acionável. A escola consegue agir antes de o problema se consolidar em reprovação.

### J.2 Sobre a evolução do projeto

**O projeto sempre foi tabular?**  
Não. O projeto começou com uma hipótese orientada a grafos, passou por PCA, classificadores tradicionais e LSTM, e terminou em uma pipeline tabular temporal.

**Por que a abordagem por grafos não foi mantida?**  
Porque o problema principal se mostrou mais aderente à previsão temporal em dados tabulares. As relações existiam, mas o sinal útil para prever a próxima nota apareceu com mais clareza em atributos temporais.

**O Random Forest foi descartado?**  
Não. Ele permaneceu como modelo candidato relevante e como etapa importante da trajetória do trabalho, embora o HistGradientBoosting tenha apresentado melhor desempenho nos resultados finais.

### J.3 Sobre a metodologia

**Que tipo de pesquisa é este TCC?**  
É uma pesquisa aplicada, predominantemente quantitativa, com objetivos exploratórios e explicativos, e procedimentos bibliográficos, documentais e experimentais.

**O trabalho pode ser considerado um estudo de caso?**  
Sim, em sentido aplicado, porque a solução foi construída e avaliada com base em dados institucionais reais de contexto escolar.

**Como a metodologia foi validada?**  
Por comparação de modelos e baselines, validação temporal por anos letivos, análise de erro e verificação da utilidade institucional dos relatórios.

### J.4 Sobre os dados

**Que dados o projeto utiliza?**  
Notas, faltas, pagamentos e dados acadêmicos e cadastrais relacionados ao contexto escolar.

**Os dados são sensíveis?**  
Sim. Por isso o projeto incorporou uma etapa de anonimização e trata a previsão como apoio à decisão, e não como julgamento automático.

**Por que os alunos aparecem como “Aluno 00505” e semelhantes?**  
Porque a base atual foi pseudonimizada para proteger a identidade real dos estudantes.

**O sistema exige um ano completo de histórico?**  
Não. A elegibilidade mínima é definida por quantidade de registros anteriores na disciplina, e não por um ano inteiro.

**Qual é a regra mínima de histórico?**  
Com 1 registro anterior há avaliação preliminar. Com 2 registros anteriores há avaliação confiável. Com 3 ou mais há avaliação robusta, embora esse corte ainda reduza demais a base em alguns cenários experimentais.

### J.5 Sobre a arquitetura e a pipeline

**O que a pipeline faz de ponta a ponta?**  
Ela prepara os dados, integra fontes, cria atributos temporais, seleciona modelos, executa validação temporal, gera predições, analisa erro e produz relatórios escolares.

**Quais são os modos principais da pipeline?**  
Previsão da próxima nota e alerta de risco pedagógico.

**Por que separar em dois modos?**  
Porque os experimentos mostraram que o melhor corte de histórico e o melhor comportamento do modelo não são os mesmos para regressão de nota e para classificação de risco.

**O que o `run_full_reporting_pipeline` faz?**  
Executa os dois modos principais da pipeline e depois gera os relatórios escolares consumidos por professor, coordenação e secretaria.

### J.6 Sobre os modelos

**O projeto usa apenas Random Forest?**  
Não. O projeto compara Random Forest, HistGradientBoosting e baselines heurísticos temporais.

**Quais modelos de regressão foram usados?**  
HistGradientBoostingRegressor, RandomForestRegressor e baselines como última nota e média das últimas notas.

**Quais modelos de classificação foram usados?**  
HistGradientBoostingClassifier, RandomForestClassifier e baselines heurísticos temporais.

**Por que manter baselines simples no pipeline?**  
Porque um baseline forte ajuda a verificar se o ganho do modelo mais sofisticado é real. Em educação aplicada, uma heurística simples pode continuar útil se for muito competitiva.

### J.7 Sobre as métricas e os resultados

**O que é MAE?**  
É o erro médio absoluto. Indica quantos pontos, em média, a previsão da nota errou em relação ao valor real.

**O que é RMSE?**  
É a raiz do erro quadrático médio. Ele pune mais fortemente erros grandes.

**O que significa acerto <= 0.5?**  
É a proporção de casos em que a previsão ficou a no máximo meio ponto da nota real.

**O que são precision, recall e F1?**  
São métricas da classificação de risco. Precision mede quantos alertas realmente eram risco, recall mede quantos casos reais de risco foram capturados, e F1 resume o equilíbrio entre essas duas dimensões.

**Quais foram os principais resultados do modo previsão de nota?**  
O melhor cenário atual atingiu MAE de 0,7601, RMSE de 1,0434 e acerto dentro de meio ponto em cerca de 46,13% dos casos no teste temporal.

**Quais foram os principais resultados do modo alerta de risco?**  
O melhor cenário atual atingiu precision de 0,6540, recall de 0,8618 e F1 de 0,7437 no teste temporal.

**Esses resultados são bons?**  
Sim para um TCC aplicado com base escolar real e heterogênea. O projeto supera baselines, utiliza validação temporal e entrega utilidade institucional concreta.

**O projeto já acerta 95%?**  
Não no sentido de prever exatamente a nota. Essa meta não é realista para a base atual em um problema escolar tão heterogêneo. O projeto entrega melhoria consistente sobre baselines e bom desempenho no alerta de risco.

### J.8 Sobre os relatórios e o dashboard

**O que o relatório do professor mostra?**  
Aluno, disciplina, nota atual, nota prevista, variação esperada, nível de risco, fatores de alerta e recomendação pedagógica.

**O que o relatório da coordenação mostra?**  
Agrupamentos por série e disciplina, taxa de alto risco, médias previstas e casos prioritários para ação institucional.

**O que o relatório da secretaria mostra?**  
Sinais administrativos relevantes, principalmente faltas e pendências financeiras, para apoiar contato preventivo e organização interna.

**O que é o ranking executivo?**  
É uma priorização consolidada de alunos com base em risco pedagógico, desempenho previsto, faltas e fatores administrativos.

**O dashboard em Streamlit faz parte do TCC?**  
Sim. Ele foi criado como camada visual para consulta dos relatórios por perfil de usuário escolar.

### J.9 Sobre ética, limites e continuidade

**O sistema pode substituir o professor?**  
Não. O professor continua sendo a autoridade pedagógica. O sistema apenas ajuda a antecipar casos que merecem atenção.

**O sistema pode produzir vieses ou injustiça?**  
Pode, se for usado sem contexto. Por isso o trabalho enfatiza anonimização, interpretação cuidadosa, validação temporal e apoio à decisão humana.

**Quais são as principais limitações do trabalho?**  
Ausência de algumas variáveis contextuais, falta de calendário escolar estruturado, histórico curto para parte dos alunos e ausência plena do vínculo de professor na base operacional atual.

**O projeto já está pronto para produção definitiva?**  
Ainda não como solução institucional final. Ele está forte como TCC aplicado e como protótipo funcional de utilidade prática, mas ainda precisa amadurecer em governança de dados e enriquecimento de contexto.

**Qual é a principal contribuição científica do trabalho?**  
Mostrar que, neste contexto escolar, uma arquitetura tabular temporal com validação temporal e camada operacional de relatórios é mais adequada do que a hipótese inicial puramente relacional.

**Qual é a principal contribuição prática do trabalho?**  
Entregar uma pipeline reproduzível que transforma dados escolares em previsões e relatórios utilizáveis por professor, coordenação e secretaria.

### J.10 Perguntas de defesa e resposta curta

**Por que o projeto mudou tanto ao longo do tempo?**  
Porque amadureceu metodologicamente. As mudanças foram guiadas por evidência empírica e aderência ao problema real.

**Por que o resultado não é perfeito?**  
Porque o objetivo do TCC não era prometer perfeição, mas construir uma solução tecnicamente válida, eticamente cuidadosa e institucionalmente útil com dados reais e limitações reais.

**Qual é a frase central do trabalho?**  
Dados escolares históricos podem ser transformados em alertas pedagógicos mais precoces quando tratados em uma pipeline temporal reproduzível, interpretável e orientada ao uso institucional.
