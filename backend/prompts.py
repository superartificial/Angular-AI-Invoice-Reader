input_prompt='''
You are an expert in understanding invoices, as well as an top tier software developer. We will upload an image as invoice and you will have to convert it to json format, based on this example:

{
  "invoice_number": "TECH-2023-04-25",
  "invoice_date": "2023-04-25",
  "amount": 3500.00,
  "tax": 350.00,
  "invoice_lines": [
    {
      "description": "Server Hardware",
      "count": 1,
      "unit_cost": 2500.00,
      "line_amount": 2500.00
    },
    {
      "description": "Network Switches",
      "count": 2,
      "unit_cost": 500.00,
      "line_amount": 1000.00
    }
  ],
  "payor": {
    "name": "XYZ Technologies",
    "address_line1": "789 Silicon St",
    "address_line2": null,
    "address_city": "Techville",
    "address_country": "USA",
    "address_postcode": "54321",
    "phone_number": "(987) 654-3210",
    "email": "purchasing@xyztechnologies.com"
  },
  "payee": {
    "name": "Tech Gear Solutions",
    "address_line1": "456 Circuit Rd",
    "address_line2": null,
    "address_city": "Electronville",
    "address_country": "USA",
    "address_postcode": "12345",
    "phone_number": "(123) 456-7890",
    "email": "sales@techgearsolutions.com"
  },
  "ai_comments": "Put comments about parts of the invoice that were hard to read, if it isn't an invoice, or other problems, here."      
}
After generating the data, run another pass through to double check the all of the information is correct, and that you have included all invoice lines. Make any amendments necessary.

Ensure all dates are in the yyyy-mm-dd format. 

The ai_comments should be notes on any issues you encountered interpretting the invoice data. If the image does not appear to be an invoice, make the invoice object null and return a note in ai_comments saying what you think it is. If there are no issues just leave this blank, don't make them up or copy the example one.

Return a maximum of eight invoice item lines, ignore any after this but leave an apologetic (indicate you are sorry) note in ai_comments telling the user that some lines have been excluded because of the limitations of the AI system. 

'''

position_prompt = '''

You are an expert in understanding invoices, as well as an top tier software developer. 

We have already extracted the data from this invoice. What we would like you to do is give the x and y pixel position from the top left of the image,

However instead of returning just the value for each json element, return a dictionary { value: str, x: number, y: number}. The pixel position should be the number of pixes from top left of the document, where the data item was found. 


'''
