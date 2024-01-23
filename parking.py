import json
import random
from typing import List, Optional

import boto3


class Car:
    def __init__(self, license_plate: str):
        self.license_plate = license_plate

    def park(self, parking_lot: List[Optional["Car"]], spot: int) -> str:
        """
        Parks the car in the specified spot if it's vacant.

        Args:
        parking_lot (List[Optional["Car"]]): The parking lot to park the car in.
        spot (int): The spot number to park the car in.

        Returns:
        str: A status message indicating the success or failure of parking.
        """
        if parking_lot[spot] is not None:
            return f"{self} could not park in spot {spot}, already occupied!"
        parking_lot[spot] = self
        return f"{self} parked successfully in spot {spot}"

    def __str__(self):
        return f"Car with license plate {self.license_plate}"


class ParkingLot:
    def __init__(self, square_footage: int, spot_length: int = 8, spot_width: int = 12):
        self.spot_size = spot_length * spot_width
        self.total_spots = square_footage // self.spot_size
        self.parking_lot = [None] * self.total_spots

    def map_vehicles(self) -> dict[int, str]:
        """
        Maps the parked vehicles to their corresponding spots.

        Returns:
        dict[int, str]: A dictionary where keys are spot numbers and values are license plates.
        """
        vehicle_map = {}
        for spot, car in enumerate(self.parking_lot):
            if car is not None:
                vehicle_map[spot] = car.license_plate
        return vehicle_map

    def save_to_file(self, filename: str = "default.json") -> None:
        """
        Saves the vehicle map to a JSON file.

        Parameters:
        - filename (str): The name of the file to save the vehicle map.

        Returns:
        None
        """
        vehicle_map = self.map_vehicles()
        with open(filename, "w") as f:
            json.dump(vehicle_map, f)

    @staticmethod
    def upload_to_s3(filename: str = "default.json", bucket_name: str = "default_bucket") -> None:
        """
        Uploads a file to an S3 bucket.

        Parameters:
        - filename (str): The name of the file to upload
        - bucket_name (str): The name of the S3 bucket.

        Returns:
        None
        """
        s3 = boto3.client("s3")
        with open(filename, "rb") as data:
            s3.upload_fileobj(data, bucket_name, filename)


def main():
    square_footage = int(input("Enter parking lot size (square footage): "))
    parking_lot = ParkingLot(square_footage)

    num_cars = int(input("Enter number of cars: "))
    cars = [Car(f"ABC{random.randint(1000000, 9999999)}") for _ in range(num_cars)]

    parked_count = 0
    while cars and not all(car is not None for car in parking_lot.parking_lot):
        car = cars.pop()
        spot = random.randint(0, len(parking_lot.parking_lot) - 1)
        while parking_lot.parking_lot[spot] is not None:
            spot = random.randint(0, len(parking_lot.parking_lot) - 1)
        print(car.park(parking_lot.parking_lot, spot))
        parked_count += 1

    if not cars:
        print(f"All cars parked, {parked_count} cars in total.")

    un_parked_car = len(cars)
    if un_parked_car > 0:
        print(f"Parking lot full, only {parked_count} cars parked. un-parked car counts {un_parked_car}")

    # Optional bonus
    vehicle_map = parking_lot.map_vehicles()
    print("Vehicle Map:", vehicle_map)
    parking_lot.save_to_file()


if __name__ == "__main__":
    main()
