import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import textwrap

ur1= "https://books.toscrape.com"

response= requests.get (ur1)
soup= BeautifulSoup(response.text, "html.parser")

books= soup.find_all("article",class_="product_pod")
book_data=[]
for book in books:
    title=book.h3.a["title"]
    price_text= book.find("p",class_="price_color").text
    price= float(price_text.replace("£", "").replace("Â", ""))

    book_data.append({
        "Title": title,
        "Price": price
    })

dF= pd.DataFrame(book_data)
dF.to_excel("Book_price.xlsx", index=False)
most_expensive= dF.loc[dF["Price"].idxmax()]

cheapest= dF.loc[dF["Price"].idxmin()]

top_books=dF.sort_values("Price",ascending=False).head(10)

wrapped_titles=[
    "\n".join(textwrap.wrap(title, 15))
    for title in top_books["Title"]

]

plt.figure(figsize=(14,8))
plt.bar(wrapped_titles, top_books["Price"])

plt.title("Top 10 Most Expensive Books")
plt.xlabel("Books")
plt.ylabel("Price (£)")
plt.xticks(rotation=0 , fontsize=8)

plt.tight_layout()

plt.savefig("book_price_chart.png")
plt.close()

pdf=FPDF()
pdf.add_page()

pdf.set_font("Arial","B",16)
pdf.cell(0,10,"Book Price Scraper Report", ln=True)

pdf.ln(10)

pdf.set_font("Arial","",12)
pdf.cell(0,10,f"Total Books Scraped: {len(dF)}", ln=True)
pdf.multi_cell(
    0,
    10,
    f"Most Expensive Book: {most_expensive["Title"]}",
    
)

pdf.multi_cell(
    0,
    10,
    f"Cheapest Book:{cheapest["Title"]}",
    

)

pdf.multi_cell(
    0,
    10,
    f"Lowest Price : £{cheapest["Price"]:.2f}",


)

pdf.ln(10)

pdf.image("book_price_chart.png", w=180)

pdf.ln(10)

pdf.multi_cell(
    0,
    10,
    "This project automatically scrapes book price data from a website,"
    "exports the data to Excel, creates a visualization chart,"
    "and generates a professional PDF report."

)

pdf.output("book_price_report.pdf")

print("Book price scraping report generated successfully.")