# GIRO APP

Sistema web simples para controlar estoque, investimento, preco de venda, lucro previsto e produtos vendidos.

## Como usar

Rode o servidor com:

```powershell
python app.py
```

Depois acesse `http://127.0.0.1:8000`.

No Render, o app usa SQLite no servidor e sincroniza PC e celular pela rota `/api/data`. O navegador ainda guarda uma copia local de seguranca caso a internet falhe.

## Funcoes

- Cadastro de produto com foto.
- Edicao e exclusao.
- Marcacao de produto como vendido.
- Reserva de produto sem dar baixa como vendido.
- Campo de gastos extras para calcular lucro real.
- Campos de taxa, frete, tempo gasto, origem da compra, plataforma e codigo interno.
- Campo de cliente/contato.
- Margem de lucro por produto.
- Lucro por hora para saber se a revenda valeu o tempo.
- Fluxo de status: pronto, reservado, anunciado, vendido, separar/embalar, enviado e entregue.
- Copiar anuncio pronto para divulgar.
- Abrir WhatsApp com o texto do anuncio.
- Duplicar produto para cadastrar itens parecidos mais rapido.
- Busca, filtro por status e ordenacao.
- Dashboard com receita, lucro, margem e ROI por periodo.
- Interface com menu lateral estilo app: Inicio, Estoque, Vendas, Capital, Calculadora, Fornecedores, Clientes, Garantias, Relatorios e Configuracoes.
- Grafico de lucro dos ultimos 7 dias.
- Ranking de produtos mais lucrativos.
- Painel de status do giro e plataformas.
- Meta mensal com barra de progresso.
- Produtos parados para identificar itens sem giro.
- Marketplace no modo garimpo, mostrando produtos com preco-alvo para comprar, revenda estimada, lucro, ROI e buscas diretas no Facebook Marketplace.
- Meu Capital redesenhado com capital atual, inicial, investido, retornado e tempo medio.
- Calculadora redesenhada como simulador de lucro com varejo/atacado, margem desejada, frete e volume mensal.
- Resumo de investido, venda prevista, lucro previsto e lucro realizado.
- Exportacao dos dados em JSON.
- Exportacao de relatorio CSV.
- Copia de relatorio geral para enviar no WhatsApp ou salvar.
- Importacao de backup JSON.
- Sincronizacao online entre aparelhos usando API + SQLite.

## Publicar no Render

O `render.yaml` ja esta configurado para rodar:

```text
python app.py
```
