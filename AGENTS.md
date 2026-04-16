# Instrucoes para agentes e colaboradores automatizados

Leia este arquivo antes de qualquer analise, teste, alteracao de codigo ou refatoracao neste repositorio.

## Sobre o projeto

Este projeto faz parte de um TCC voltado para analise de dados escolares com o objetivo de antecipar riscos academicos. O foco principal e prever proximas notas dos alunos e identificar sinais de alerta para apoiar o professor antes que o aluno chegue a uma situacao de reprovacao bimestral, trimestral, semestral ou anual.

As fontes de dados do projeto incluem, entre outras:
- notas
- faltas
- pagamentos
- dados cadastrais e escolares

O projeto teve uma fase inicial orientada a grafo e evoluiu para uma abordagem mais tabular com Random Forest. O proximo passo planejado e refatorar a arquitetura para uma pipeline real de dados e modelagem preditiva.

## Arquivo de registro obrigatorio

Todo teste, ajuste, experimento, refatoracao, correcao ou mudanca arquitetural deve ser descrito no arquivo:

`/Users/warley/Desktop/Development/Personal/KnowledgeGraphModelSchoolEducation/RELATORIO_TCC_PROJETO.txt`

Se uma alteracao for feita, o registro correspondente deve ser atualizado no mesmo fluxo de trabalho.

## Regras de trabalho

1. Nao alterar codigo sem antes entender em que etapa historica do projeto a mudanca se encaixa.
2. Preservar o contexto academico do TCC e registrar a motivacao tecnica de cada mudanca.
3. Priorizar explicacoes claras e rastreaveis, para que o orientador e o autor consigam entender o caminho seguido.
4. Evitar mudancas destrutivas ou reescritas amplas sem registrar:
   - problema identificado
   - decisao tomada
   - impacto esperado
5. Sempre considerar que os dados escolares possuem natureza temporal e sensivel.
6. Ao criar novos experimentos, registrar no relatorio:
   - data
   - objetivo
   - arquivos afetados
   - resumo do resultado
   - proximo passo sugerido

## Objetivo das proximas iteracoes

As proximas iteracoes devem caminhar para:
- consolidacao da narrativa do TCC
- refatoracao da arquitetura atual
- criacao de uma pipeline reproduzivel
- uniao correta entre notas, faltas e pagamentos
- validacao de modelos com criterio temporal
- geracao de alertas pedagogicos com interpretabilidade
