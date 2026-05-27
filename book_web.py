import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from pathlib import Path
import textwrap


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

URL = "https://books.toscrape.com"

BACKGROUND = "#050816"
CARD_BG = "#0B1020"
AX_BG = "#0B1020"

CYAN = "#00F5FF"
PURPLE = "#9D4EDD"
GREEN = "#39FF14"
PINK = "#FF4FD8"
YELLOW = "#FFD60A"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = "DejaVu Sans"


def scrape_books():
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    book_data = []

    for book in books:
        title = book.h3.a["title"]

        price_text = (
            book.find("p", class_="price_color")
            .text
            .replace("£", "")
            .replace("Â", "")
        )

        price = float(price_text)

        book_data.append({
            "Title": title,
            "Price": price
        })

    return pd.DataFrame(book_data)



def style_axis(ax):
    ax.set_facecolor(AX_BG)

    ax.grid(
        color="white",
        alpha=0.08,
        linestyle="--",
        linewidth=0.8
    )

    ax.tick_params(colors=WHITE, labelsize=10)

    for spine in ax.spines.values():
        spine.set_color("#27324A")

    ax.set_axisbelow(True)



def create_bar_chart(top_books):
    wrapped_titles = [
        "\n".join(textwrap.wrap(title, 14))
        for title in top_books["Title"]
    ]

    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor(BACKGROUND)

    bars = ax.bar(
        wrapped_titles,
        top_books["Price"],
        color=CYAN,
        edgecolor=PURPLE,
        linewidth=1.8,
        alpha=0.86,
        width=0.42
    )

    style_axis(ax)

    ax.set_title(
        "TOP 10 MOST EXPENSIVE BOOKS",
        fontsize=24,
        color=CYAN,
        weight="bold",
        pad=20
    )

    ax.set_xlabel("Books", fontsize=13, color=WHITE)
    ax.set_ylabel("Price (£)", fontsize=13, color=WHITE)

    plt.xticks(rotation=0)

    chart_path = OUTPUT_DIR / "book_price_chart.png"

    plt.tight_layout()

    plt.savefig(
        chart_path,
        dpi=300,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight"
    )

    plt.close()

    return chart_path



def create_pie_chart(top_books):
    top5 = top_books.head(5)

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(BACKGROUND)
    ax.set_facecolor(AX_BG)

    colors = [CYAN, PURPLE, GREEN, PINK, YELLOW]

    wedges, _ = ax.pie(
        top5["Price"],
        colors=colors,
        startangle=90,
        wedgeprops={
            "edgecolor": BACKGROUND,
            "linewidth": 2
        }
    )

    ax.legend(
        wedges,
        ["\n".join(textwrap.wrap(t, 18)) for t in top5["Title"]],
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=9,
        labelcolor=WHITE,
        frameon=False
    )

    ax.set_title(
        "TOP 5 PRICE DISTRIBUTION",
        fontsize=22,
        color=GREEN,
        weight="bold",
        pad=20
    )

    pie_path = OUTPUT_DIR / "book_pie_chart.png"

    plt.tight_layout()

    plt.savefig(
        pie_path,
        dpi=300,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight"
    )

    plt.close()

    return pie_path



def add_kpi_card(fig, x, y, w, h, title, value, color):
    
    card = Rectangle(
        (x, y),
        w,
        h,
        transform=fig.transFigure,
        facecolor=CARD_BG,
        edgecolor=color,
        linewidth=2.5,
        zorder=1
    )

    fig.patches.append(card)

    fig.text(
        x + w / 2,
        y + h * 0.66,
        title,
        ha="center",
        va="center",
        color=WHITE,
        fontsize=10,
        weight="bold",
        zorder=5
    )

    fig.text(
        x + w / 2,
        y + h * 0.34,
        value,
        ha="center",
        va="center",
        color=color,
        fontsize=18,
        weight="bold",
        zorder=5
    )


def generate_pdf(df, most_expensive, cheapest, chart_path, pie_chart_path):
    pdf_path = OUTPUT_DIR / "book_price_report.pdf"

    with PdfPages(str(pdf_path)) as pdf:

    

        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor(BACKGROUND)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        ax.set_facecolor(BACKGROUND)

        fig.text(
            0.5,
            0.91,
            "AI BOOK PRICE REPORT",
            fontsize=28,
            color=CYAN,
            ha="center",
            weight="bold",
            zorder=10
        )

        fig.text(
            0.5,
            0.855,
            "Automated Web Scraping Dashboard",
            fontsize=15,
            color=WHITE,
            ha="center",
            weight="bold",
            zorder=10
        )

        
        card_y = 0.63
        card_w = 0.19
        card_h = 0.13

        cards = [
            ("Books Scraped", f"{len(df)}", CYAN),
            ("Highest Price", f"£{most_expensive['Price']:.2f}", PURPLE),
            ("Lowest Price", f"£{cheapest['Price']:.2f}", GREEN),
            ("Average Price", f"£{df['Price'].mean():.2f}", PINK)
        ]

        xs = [0.055, 0.295, 0.535, 0.775]

        for x, (title, value, color) in zip(xs, cards):
            add_kpi_card(
                fig=fig,
                x=x,
                y=card_y,
                w=card_w,
                h=card_h,
                title=title,
                value=value,
                color=color
            )

        fig.text(
            0.5,
            0.48,
            "TOP INSIGHTS",
            fontsize=22,
            color=GREEN,
            weight="bold",
            ha="center",
            zorder=10
        )

        insights = [
            f"Most expensive book: {textwrap.shorten(most_expensive['Title'], width=72, placeholder='...')}",
            f"Cheapest book: {textwrap.shorten(cheapest['Title'], width=58, placeholder='...')}",
            "Automated scraping completed successfully",
            "Excel + PDF reports generated automatically"
        ]

        y = 0.40

        for insight in insights:
            fig.text(
                0.5,
                y,
                f"• {insight}",
                fontsize=12,
                color=WHITE,
                ha="center",
                zorder=10
            )
            y -= 0.045

        fig.text(
            0.5,
            0.105,
            "Built with Python • BeautifulSoup • Pandas • Matplotlib",
            fontsize=13,
            color=CYAN,
            ha="center",
            weight="bold",
            zorder=10
        )

        pdf.savefig(fig, facecolor=fig.get_facecolor())
        plt.close(fig)

        

        img1 = plt.imread(chart_path)

        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor(BACKGROUND)

        ax = fig.add_axes([0.03, 0.05, 0.94, 0.90])
        ax.imshow(img1)
        ax.axis("off")

        pdf.savefig(fig, facecolor=fig.get_facecolor())
        plt.close(fig)

    

        img2 = plt.imread(pie_chart_path)

        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor(BACKGROUND)

        ax = fig.add_axes([0.03, 0.05, 0.94, 0.90])
        ax.imshow(img2)
        ax.axis("off")

        pdf.savefig(fig, facecolor=fig.get_facecolor())
        plt.close(fig)

    return pdf_path




def main():
    df = scrape_books()

    excel_path = OUTPUT_DIR / "book_price_dashboard.xlsx"
    df.to_excel(excel_path, index=False)

    most_expensive = df.loc[df["Price"].idxmax()]
    cheapest = df.loc[df["Price"].idxmin()]

    top_books = (
        df.sort_values("Price", ascending=False)
        .head(10)
    )

    chart_path = create_bar_chart(top_books)
    pie_chart_path = create_pie_chart(top_books)

    pdf_path = generate_pdf(
        df=df,
        most_expensive=most_expensive,
        cheapest=cheapest,
        chart_path=chart_path,
        pie_chart_path=pie_chart_path
    )

    print("DONE")
    print(f"Excel created: {excel_path}")
    print(f"Chart created: {chart_path}")
    print(f"Pie chart created: {pie_chart_path}")
    print(f"PDF created: {pdf_path}")


if __name__ == "__main__":
    main()