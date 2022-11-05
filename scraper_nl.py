import requests
import json
import csv


# Search sets - FROM ,  TO,      DEPART,       RETURN
search_sets = (('MAD', 'AUH', '2022-04-18', '2022-04-23'),
               ('MAD', 'FUE', '2023-02-09', '2023-02-16'),
               ('JFK', 'FUE', '2022-05-15', '2022-05-28'),
               ('CPH', 'MAD', '2022-06-01', '2022-06-28'),
               ('CPH', 'AUH', '2022-07-01', '2022-07-28'),
               ('CPH', 'FUE', '2023-04-04', '2023-04-21'),
               ('MAD', 'FUE', '2023-03-09', '2023-03-11'),
               ('JFK', 'AUH', '2022-08-15', '2022-08-26'),
               ('CPH', 'MAD', '2022-09-01', '2022-09-20'),
               ('MAD', 'AUH', '2022-10-12', '2022-12-19'))

f = open('search_sets_flights.csv', 'w', newline='')
header = ("Price", "Taxes", "outbound 1 airport departure", "outbound 1 airport arrival", "outbound 1 time departure", "outbound 1 time arrival", "outbound 1 flight number", "outbound 2 airport departure", "outbound 2 airport arrival", "outbound 2 time departure", "outbound 2 time arrival", "outbound 2 flight number", "inbound 1 airport departure", "inbound 1 airport arrival", "inbound 1 time departure", "inbound 1 time arrival", "inbound 1 flight number", "inbound 2 airport departure", "inbound 2 airport arrival", "inbound 2 time departure", "inbound 2 time arrival", "inbound 2 flight number")
writer = csv.writer(f)
writer.writerow(header)

for search in search_sets:
    
    try:                           # Link is hidden, so program wont work
        html_text = requests.get('http://***/search.php?from={0}&to={1}&depart={2}&return={3}'.format(search[0],search[1],search[2],search[3])).text

        json_data = json.loads(html_text)
        total_availabilities = json_data['body']['data']['totalAvailabilities']
        journeys = json_data['body']['data']['journeys']

        outbound_flights = []
        inbound_flights = []
        combined_flights = []
        all_prices = []
        cheapest_combinations = []

        price_by_id = dict()

        for recomm in total_availabilities:
            id = recomm['recommendationId']
            price = recomm['total']
            price_by_id[id] = price

# Creating outbound flights set ------------------------------------------------------------------------------

        for index, flight in enumerate(journeys):
            if flight['direction'] == 'I' and len(flight['flights']) < 3:
                index = dict()
                index['price_comb'] = price_by_id[flight['recommendationId']]
                index['tax_out'] = flight['importTaxAdl']
                index['departure_out1'] = flight['flights'][0]['airportDeparture']['code']
                index['arrival_out1'] = flight['flights'][0]['airportArrival']['code']
                index['date_departure_out1'] = flight['flights'][0]['dateDeparture'].replace('/', '-')
                index['date_arrival_out1'] = flight['flights'][0]['dateArrival'].replace('/', '-')
                index['number_out1'] = flight['flights'][0]['companyCode'] + str(flight['flights'][0]['number'])
                if len(flight['flights']) == 1:
                    index['departure_out2'] = '-'
                    index['arrival_out2'] = '-'
                    index['date_departure_out2'] = '-'
                    index['date_arrival_out2'] = '-'
                    index['number_out2'] = '-'
                    index['direct'] = True
                else:
                    index['departure_out2'] = flight['flights'][1]['airportDeparture']['code']
                    index['arrival_out2'] = flight['flights'][1]['airportArrival']['code']
                    index['date_departure_out2'] = flight['flights'][1]['dateDeparture'].replace('/', '-')
                    index['date_arrival_out2'] = flight['flights'][1]['dateArrival'].replace('/', '-')
                    index['number_out2'] = flight['flights'][1]['companyCode'] + str(flight['flights'][1]['number'])
                    index['direct'] = False
                if index not in outbound_flights:
                    outbound_flights.append(index)

# Creating inbound flights set -------------------------------------------------------------------------------

        for index, flight in enumerate(journeys):
            if flight['direction'] == 'V' and len(flight['flights']) < 3:
                index = dict()
                index['tax_inb'] = flight['importTaxAdl']
                index['departure_inb1'] = flight['flights'][0]['airportDeparture']['code']
                index['arrival_inb1'] = flight['flights'][0]['airportArrival']['code']
                index['date_departure_inb1'] = flight['flights'][0]['dateDeparture'].replace('/', '-')
                index['date_arrival_inb1'] = flight['flights'][0]['dateArrival'].replace('/', '-')
                index['number_inb1'] = flight['flights'][0]['companyCode'] + str(flight['flights'][0]['number'])
                if len(flight['flights']) == 1:
                    index['departure_inb2'] = '-'
                    index['arrival_inb2'] = '-'
                    index['date_departure_inb2'] = '-'
                    index['date_arrival_inb2'] = '-'
                    index['number_inb2'] = '-'
                    index['direct'] = True
                else:
                    index['departure_inb2'] = flight['flights'][1]['airportDeparture']['code']
                    index['arrival_inb2'] = flight['flights'][1]['airportArrival']['code']
                    index['date_departure_inb2'] = flight['flights'][1]['dateDeparture'].replace('/', '-')
                    index['date_arrival_inb2'] = flight['flights'][1]['dateArrival'].replace('/', '-')
                    index['number_inb2'] = flight['flights'][1]['companyCode'] + str(flight['flights'][1]['number'])
                    index['direct'] = False
                if index not in inbound_flights:
                    inbound_flights.append(index)

# Creating outbound and inbound flight combinations set ------------------------------------------------------

        for out_flight in outbound_flights:
            for in_flight in inbound_flights:
                prices = dict()
                prices['full_price'] = round(out_flight['price_comb'] + out_flight['tax_out'] + in_flight['tax_inb'], 2)
                prices['price_comb'] = round(out_flight['price_comb'], 2)
                prices['full_tax'] = round(out_flight['tax_out'] + in_flight['tax_inb'], 2)
                combination = {**prices, **out_flight, **in_flight}
                del combination['tax_out']
                del combination['tax_inb']
                del combination['direct']
                combined_flights.append(combination)

# Finding cheapest price -------------------------------------------------------------------------------------

        for price in combined_flights:
            all_prices.append(price['full_price'])

        cheapest = min(all_prices)

# Creating cheapest flight combinations set and writing to file ----------------------------------------------

        for combination in combined_flights:
            if combination['full_price'] == cheapest:
                del combination['full_price']
                cheapest_combinations.append(combination)

        for combination in cheapest_combinations:
            list1 = []
            for key, value in combination.items():
                list1.append(value)
            tuple1 = tuple(list1)
            writer.writerow(tuple1)

    except:
        error = 'No flights for search set: {}\n'.format(search)
        f.write(error)

f.close()
