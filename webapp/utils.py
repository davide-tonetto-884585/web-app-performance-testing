# db result to html table
def to_html_table(col_names, data):
    table = "<table><tr>"
    for col in col_names:
        table += f"<th>{col}</th>"
    table += "</tr>"

    for row in data:
        table += "<tr>"
        for col in row:
            table += f"<td>{col}</td>"
        table += "</tr>"
    table += "</table>"

    return table
