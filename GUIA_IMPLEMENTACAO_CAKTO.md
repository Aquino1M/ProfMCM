# Guia de implementação na Cakto - Método Milionário

## Recomendação principal
Use a **Cakto Members** como porta de entrada, login e controle de acesso. Ela já possui visual de streaming, módulos, aulas, progresso, materiais, comentários e comunidade. A página `area_aluno.html` deste pacote funciona como um painel complementar e como modelo visual, mas não deve ficar pública sem proteção.

## Estrutura recomendada
1. Crie um produto chamado **Método Milionário - Formação em Cortes**.
2. Em Entrega do Produto, selecione **Cakto Members**.
3. Crie um workspace com a identidade do curso.
4. Cadastre as trilhas na ordem abaixo:
   - Comece por aqui: Módulos 0 e 1
   - Clipador Iniciante: Módulos 2 a 7
   - Aceleração: Módulos Extra 1 e Extra 2
   - Profissional: Módulo Agência e Módulo Operação
   - Biblioteca Estratégica: nove aulas bônus do Blog Real Oficial
5. Em cada aula, adicione:
   - vídeo ou aula gravada;
   - texto curto com objetivo e entrega;
   - PDF do módulo como material complementar;
   - atividade prática no final.
6. Ative liberação gradual apenas se fizer parte da sua estratégia. Uma sugestão é liberar um módulo por dia nos fundamentos e manter os bônus liberados após o Módulo 3.

## Como usar a área digital criada
### Opção A - Recomendada
Use a Cakto Members como área principal. Copie a organização e os textos de `area_aluno.html`, faça upload dos PDFs e mantenha o login totalmente dentro da Cakto.

### Opção B - Painel complementar
Hospede esta pasta em Vercel, Netlify ou hospedagem própria. Dentro da primeira aula privada da Cakto, coloque um botão para o endereço de `area_aluno.html`. O aluno já terá passado pelo login da Cakto, mas o endereço externo ainda pode ser compartilhado; para segurança real, proteja a hospedagem com autenticação.

### Opção C - Área externa completa
Selecione área de membros externa na Cakto e implemente backend, banco de dados e webhook de compra aprovada para criar e revogar acessos. O HTML deste pacote é somente a interface; ele não substitui autenticação segura.

## Materiais por módulo
Os arquivos estão em `materiais_modulos/`. Faça upload do PDF correspondente em cada módulo. O bônus novo é `bonus_estrategias_real_oficial.pdf`.

## Padrão de aula para copiar
**Objetivo:** o que o aluno conseguirá fazer.

**Antes de assistir:** baixe o material e abra o projeto de prática.

**Durante a aula:** pause nos momentos de demonstração e repita o passo.

**Atividade:** execute o exercício descrito no material.

**Entrega:** envie print, link, vídeo ou documento solicitado.

**Conclusão:** marque a aula somente depois da entrega.

## Avisos importantes
- Evite prometer renda ou viralização garantida.
- Regras de monetização e distribuição mudam; revise as aulas periodicamente.
- Trabalhe com conteúdo próprio, autorizado ou fornecido pelo cliente.
- Benchmarks do blog devem virar hipóteses de teste, não regras universais.
