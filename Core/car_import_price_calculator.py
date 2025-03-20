
def count_import_price_estimation(car_price, car_volume, car_age, horse_power, car_type : str):
    #recoded this methodology from website https://calcus.ru/rastamozhka-auto
    #it is faster to recode it than to use selenium + their api is not free and defended
    import_oformlenie = _get_arrs_(car_price,
                                   [200000, 450000, 1200000, 2700000, 4200000, 5500000, 7000000],
                                   [1067, 2134, 4269, 11746, 16524, 21344, 27540, 30000]
                                   )
    horse_power_price_akciz = (_get_arrs_(horse_power, [90, 150, 200,300,400,500],
                                   [0, 61, 583,955,1628,1685,1740])*
                         horse_power)

    immport_tarif_poshlina = 0
    if car_type == 'petrol':
        immport_tarif_poshlina = _get_petrol_car_tarif_coed(car_price, car_volume, car_age)
    if car_type == 'diesel':
        immport_tarif_poshlina = _get_diesel_car_tarif_coed(car_price, car_volume, car_age)
    if car_type == 'electro':
        immport_tarif_poshlina = 0.15*car_price

    util_gathering = 0
    if car_type != 'electro':
        if car_age<3:
            util_gathering = _get_arrs_(car_volume,
        [1000, 2000, 3000, 3500],
        [9.01, 33.37, 93.77, 107.67, 137.11])
        else:
            util_gathering = _get_arrs_(car_volume,
        [1000, 2000, 3000, 3500],
        [23,58.7,141.97,165.84,180.24])
    else:
        if car_age<3:
            util_gathering = 33.37
        else:
            util_gathering = 58.7

    util_gathering *=20000

    nds = (horse_power_price_akciz + car_price + immport_tarif_poshlina)*0.2
    return import_oformlenie +immport_tarif_poshlina +horse_power_price_akciz+ nds+util_gathering



def _get_arrs_(parameter, parameter_array, output_parameter_array):
    '''When you have a table with 1 parameter and many varying fixed results based on it (tarifs, for example),
    this method will make life easier '''
    if parameter >= parameter_array[-1]:
        return output_parameter_array[-1]
    for i in len(parameter_array):
        if parameter < parameter_array[i]:
            return output_parameter_array[i]


def _get_petrol_car_tarif_coed(car_price, car_volume, car_age):
    tarif_bounndries = [1000, 1500, 1800, 2300, 2800, 3000]
    if car_age < 3:
        tarifs_per_price = [0.15, 0.15, 0.15, 0.15, 0.15, 0.125, 0.125]
        return _get_arrs_(car_volume, tarif_bounndries, tarifs_per_price) * car_price
    elif car_age < 7:
        tarifs_per_price = [0.15, 0.15, 0.15, 0.15, 0.15, 0.125, 0.125]
        tarifs_euro_per_liter = [0.36, 0.4, 0.36, 0.44, 0.44, 0.44, 0.8]
        price_for_price = _get_arrs_(car_volume, tarif_bounndries, tarifs_per_price) * car_price
        price_for_volume = _get_arrs_(car_volume, tarif_bounndries, tarifs_euro_per_liter)  # in euros need
        return max(price_for_price, price_for_volume)
    else:
        tarifs_euro_per_liter = [1.4, 1.5, 1.6, 2.2, 2.2, 2.2, 3.2]
        return _get_arrs_(car_volume, tarif_bounndries, tarifs_euro_per_liter)  # in euros needs conversion


def _get_diesel_car_tarif_coed(car_price, car_volume, car_age):
    tarif_bounndries = [1500,2500]
    if car_age < 3:
        tarifs_per_price = [0.15, 0.15, 0.15]
        return _get_arrs_(car_volume, tarif_bounndries, tarifs_per_price)* car_price
    elif car_age < 7:
        tarifs_per_price = [0.20, 0.20, 0.20]
        tarifs_euro_per_liter = [0.32, 0.4, 0.8]
        price_for_price = _get_arrs_(car_volume, tarif_bounndries, tarifs_per_price) * car_price
        price_for_price = _get_arrs_(car_volume, tarif_bounndries, tarifs_per_price) * car_price
        price_for_volume = _get_arrs_(car_volume, tarif_bounndries, tarifs_euro_per_liter)  # in euros need
        return max(price_for_price, price_for_volume)
    else:
        tarifs_euro_per_liter = [1.5, 2.2, 3.2]
        return _get_arrs_(car_volume, tarif_bounndries, tarifs_euro_per_liter)  # in euros needs conversion #TODO


