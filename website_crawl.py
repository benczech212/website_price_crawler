from bs4 import BeautifulSoup
import pandas as pd

def parse_local_html(file_path):
    # Open and read the local HTML file
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find and extract the desired elements (updated for error handling)
    products = soup.select('.item.product.product-item')

    product_data = []

    for product in products:
        product_info = {}

        # Check if the element is found before accessing its text attribute
        brand_element = product.select_one('.product-item-brand a')
        product_info['Brand'] = brand_element.text.strip() if brand_element else "N/A"

        title_element = product.select_one('.product-item-name span')
        product_info['Title'] = title_element.text.strip() if title_element else "N/A"

        strain_element = product.select_one('.strain_info_value')
        product_info['Strain'] = strain_element.text.strip() if strain_element else "N/A"

        thc_element = product.select_one('.thc-info-data')
        product_info['THC Percentage'] = float(thc_element.text.strip().rstrip('%')) if thc_element else "N/A"

        price_box = product.select_one('.price-box')

        if price_box:
            regular_price_element = price_box.select_one('.old-price .price')
            sale_price_element = price_box.select_one('.special-price .price')

            if sale_price_element:
                product_info['Regular Price'] = float(regular_price_element.text.replace('$', '').strip()) if regular_price_element else "N/A"
                product_info['Sale Price'] = float(sale_price_element.text.replace('$', '').strip()) if sale_price_element else "N/A"
                product_info['On Sale'] = True
            else:
                product_info['Regular Price'] = float(price_box.select_one('.price-container .price').text.replace('$', '').strip()) if price_box.select_one('.price-container .price') else "N/A"
                product_info['Sale Price'] = "N/A"
                product_info['On Sale'] = False
        else:
            product_info['Regular Price'] = "N/A"
            product_info['Sale Price'] = "N/A"
            product_info['On Sale'] = False

        # Extract the image URL
        img_url = product.select_one('.product-image-photo')['src'] if product.select_one('.product-image-photo') else "N/A"
        product_info['Image URL'] = img_url if img_url.startswith('http') else f"https:{img_url}"

        product_data.append(product_info)

    df = pd.DataFrame(product_data)

    # Extract weight from the title using regular expressions
    df['Weight'] = df['Title'].str.extract(r'(\d+(\.\d+)?)\s*[gG]').astype(float).groupby(level=0)[0].last().astype(float)

    # Filter rows where 'Weight' is not NaN
    df = df[df['Weight'].notna()]

    # Filter rows where 'THC Percentage' and 'Price' are not 'N/A'
    df = df[(df['THC Percentage'] != 'N/A') & (df['Regular Price'] != 'N/A')]

    # Calculate the 'Value' column
    df['Value'] = (df['Weight'] * df['THC Percentage'] / df['Regular Price']).fillna(0)

    # Sort the DataFrame by the 'Value' column
    df = df.sort_values(by='Value', ascending=False)

    # Export the DataFrame to a CSV file
    df.to_csv('sorted_results.csv', index=False)

    return df

# Specify the path to the local HTML file
html_file_path = "./html_page.html"  # Replace with the actual file path

# Parse the local HTML file and get the DataFrame
df = parse_local_html(html_file_path)

# Display the DataFrame
print(df)
