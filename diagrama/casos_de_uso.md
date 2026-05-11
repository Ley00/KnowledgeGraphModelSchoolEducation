# Casos de Uso

Este diagrama mostra quem interage com a solução e quais objetivos cada perfil tem dentro do projeto.

```mermaid
flowchart LR
    Professor["Professor"]
    Coordenacao["Coordenação"]
    Secretaria["Secretaria"]
    Pesquisador["Pesquisador / Desenvolvedor"]
    Operador["Operador de dados"]

    UC1(("Preparar banco restaurado"))
    UC2(("Extrair dados para CSV"))
    UC3(("Rodar pipeline preditiva"))
    UC4(("Comparar cenários de histórico"))
    UC5(("Gerar relatórios escolares"))
    UC6(("Consultar dashboard"))
    UC7(("Acompanhar alunos em risco"))
    UC8(("Priorizar ações pedagógicas"))
    UC9(("Acompanhar sinais administrativos"))

    Operador --> UC1
    Operador --> UC2
    Pesquisador --> UC3
    Pesquisador --> UC4
    Pesquisador --> UC5
    Professor --> UC6
    Professor --> UC7
    Coordenacao --> UC6
    Coordenacao --> UC8
    Secretaria --> UC6
    Secretaria --> UC9

    UC2 --> UC3
    UC3 --> UC5
    UC5 --> UC6
```

## Leitura rápida

- o operador técnico mantém o banco e a extração dos dados.
- o pesquisador ou desenvolvedor usa a CLI para rodar e avaliar a pipeline.
- professor, coordenação e secretaria consomem o resultado final por relatórios e dashboard.
- cada perfil usa a solução com uma finalidade diferente, mesmo partindo da mesma base analítica.
