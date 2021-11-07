import requests
from bs4 import BeautifulSoup
from Artigo import Artigo
import csv

def get_article(url):
    url = 'https:' + url
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    iframe_url = soup.find('iframe')['src']
    page = requests.get(iframe_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    url = 'https://forms.camara.leg.br/' + soup.find('a')['href']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    url = soup.find('a', attrs={'class': 'enquete-descricao__link'})['href']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    if soup != None:
        return extrai_dados_do_artigo(soup)

    return ''

def extrai_dados_do_artigo(soup):
    titulo = soup.find('h1', attrs={'class': 'g-artigo__titulo'}).text
    print('-->', titulo)

    sub_titulo = ''
    sub_titulo_element = soup.find('p', attrs={'class': 'g-artigo__descricao'})
    if sub_titulo_element != None:
        sub_titulo = sub_titulo_element.text

    data_hora = soup.find('p', attrs={'class': 'g-artigo__data-hora'}).text

    div = soup.find('div', attrs={'class': 'js-article-read-more'})
    resultado = ''
    paragrafos = div.find_all('p', attrs={'class': None})
    
    for p in paragrafos:
        resultado += p.text.strip().replace('\n', '')

    return Artigo(titulo, sub_titulo, data_hora, resultado, 0)


def get_dados_votacao(url):
    url = 'https://www.camara.leg.br/internet/votacao/' + url
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    #print(f'Pagina voto: {url}')

    titulo = " ".join(soup.find_all('p')[2].text.split())
    print('Titulo: ', titulo)

    div = soup.find('div', attrs={'id': 'corpoVotacao'})
    inicio_votacao = div.find(
        "strong", text="Início da votação: ").next_sibling
    print(f'\nInício votação: {inicio_votacao.strip()} ')

    itens = ','.join([''.join([item.previous_sibling, item.text, item.next_sibling])
                      for item in soup.select(".coluna1")])
    infoVotacao = ' '.join(itens.split()).replace(",", "\n")
    print(f'\nDados Votacao:\n {infoVotacao} ')

    listaVotacao = soup.find('div', attrs={'id': 'listagem'})
    table = listaVotacao.find('table', attrs={'class': 'tabela-2'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    voto = ""
    lista_voto = ""
    for row in rows:
        if row.find('th') != None:
            estado = row.text.strip()
        else:
            for td in row.find_all('td'):
                voto = voto + " " + td.text.strip()
            lista_voto = lista_voto + " " + estado + " " + voto + "\n"
        voto = ""

    #print(f'\nVotos: {lista_voto}')
    return titulo

def post_page():
    base_url = 'https://www.camara.leg.br/internet/votacao/default.asp'

    post_data = {'OutroMes': '01/11/2021'}
    page = requests.post(base_url, data=post_data)
    soup = BeautifulSoup(page.content, 'html.parser')

    #with open("myfile.html", "w") as file:
    #    file.write(page.content)

    lis = soup.find_all('li', attrs={ 'class': None })
    pegou_artigo = False
    artigos = []
    titulos = []

    for li in lis:
        if li.find('a') != None:
            url = li.find('a')['href']
            text = li.find('a').text.strip()

            if text.startswith('PL') or text.startswith('PEC') or text.startswith('PLP'):
                print('----' * 10)
                artigo = get_article(url)

                if artigo == '':
                    pegou_artigo = False
                    print('Artigo não encontrado')
                else:
                    pegou_artigo = True

            if pegou_artigo and text.startswith('Relação de votantes por UF'):
                pegou_artigo = False
                artigo.titulo = get_dados_votacao(url)
                artigos.append(artigo)
    
    # open the file in the write mode
    with open('artigos.csv', 'w', encoding='UTF8', newline='') as file:
        # create the csv writer
        writer = csv.writer(file)

        writer.writerow(['titulo', 'sub-titulo', 'paragrafos', 'votos_publicos'])

        for artigo in artigos:
            # write a row to the csv file
            writer.writerow([artigo.titulo, artigo.sub_titulo, artigo.paragrafos, artigo.quantidade_de_votos_publicos])


post_page()
