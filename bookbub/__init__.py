import requests
from lxml import html
from time import sleep
from random import uniform
from mongoengine import *
from mongoengine.fields import ListField
from pushbullet import Pushbullet
import argparse

BASE_URL='https://www.bookbub.com'

def cmd_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("api_key")
	args = parser.parse_args()
	return str(args.api_key)

def geturl(page):
	url='https://www.bookbub.com/ebook-deals/free-ebooks?page='
	return url+str(page+1)

class free_ebook(Document):
    title=StringField(default = "")
    description=StringField(default = "")
    path_url=StringField(default = "")
    buy_url=ListField(default = [])
	
def title(tree):
	xpath='//div/h5[@class="standard book-title"]/span'
	elems=tree.xpath(xpath)
	return elems[0]

def path(tree):
	xpath='//div/h5/a/@href'
	elems=tree.xpath(xpath)
	return elems

def storepath(tree):
	xpath='//div[@class="primary-retailer-links retailer-links retailers vertical-1"]/a/@href'
	elems=tree.xpath(xpath)
	return elems

def descrip(tree):
	xpath='//div[@class="blurb"]'
	elems=tree.xpath(xpath)
	return elems[0]

def publisherdescrip(tree):
	xpath='//*[@id="book-detail-content"]/div[4]/div/div[2]/div/span[1]'
	elems=tree.xpath(xpath)
	desc=''
	print (elems)
	for elem in elems:
		desc=desc+(elem.text_content().strip())
	return desc



def run():
	for page in range(3):
		api_key = cmd_parser()
		pb = Pushbullet(api_key)
		current_list = ""
		data=requests.get(geturl(page))
		tree=html.document_fromstring(data.content)
		paths=path(tree)

		for pathee in paths:
			one_book = ""
			book=free_ebook()
			print("\n")
			print ("PAGE:"+str(page))
			sleep(uniform(1,2))
			book_url=BASE_URL+pathee
			data=requests.get(book_url)
			tree=html.document_fromstring(data.content)
			print (book_url)
			titles=title(tree)
			storepaths=storepath(tree)
			description=descrip(tree)


			one_book+= "\n\n\nTITLE:"+titles.text_content().strip()
			one_book+= "\nLINK:"+BASE_URL+pathee
			one_book+= "\nDESCRIPTION:"+description.text_content().strip()
			one_book+= "\nBUY FROM:"
			for storepathee in storepaths:
				one_book+='\n'
				one_book+= (storepathee)
			book.title=titles.text_content().strip()
			book.description=description.text_content().strip()
			book.path_url=book_url
			book.buy_url.append(storepathee)
			

			print (one_book)
			current_list+="\n***********************************************************************************\n"
			current_list+=one_book
			print ("\n")
			storepathee=None
			storepaths=None
			titles=None
			sleep(uniform(5,10))

		data=None
		tree=None
		paths=[]
		push = pb.push_note("Free Ebooks", current_list)

