import json
import os
from typing import Set, Dict


class ServiceRegion(object):
    def __init__(self, name: str, sb_region: str, location: str, service: str, emoji: str):
        self.name = name
        self.sb_region = sb_region
        self.location = location
        self.service = service
        self.emoji = emoji

    def __repr__(self):
        return 

    @classmethod
    def generate_from_lookup(cls, service_region_name: str):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "service_region_info.json")

        with open(file_path) as regions_data:
            regions = json.load(regions_data)

        service_region_info = regions[service_region_name]

        return cls(
            service_region_name,
            service_region_info['sb_region'],
            service_region_info['location'],
            service_region_info['service'],
            service_region_info['emoji']
        )


class Region(object):
    def __init__(self, region_name: str):
        self.region_name = region_name
        service_regions = self.generate_service_regions()
        self.aws_regions = service_regions["AWS"]
        self.azure_regions = service_regions["Azure"]
        self.gcp_regions = service_regions["GCP"]
        self.regions = {
            "aws": self.aws_regions,
            "azure": self.azure_regions,
            "gcp": self.gcp_regions,
        }

    def __repr__(self):
        return self.region_name

    def generate_service_regions(self) -> Dict[str, ServiceRegion]:
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "region_info.json")

        with open(file_path) as regions_data:
            regions = json.load(regions_data)

        sb_region = regions[self.region_name]

        region_services = []
        for key in sb_region:
            region_services.append(key)

        service_regions = {}
        for service in region_services:
            service_regions[service] = []
            for region in sb_region[service]:
                new_service_region = ServiceRegion(
                    region["name"],
                    self.region_name,
                    region["location"],
                    service, region["emoji"]
                )
                service_regions[service].append(new_service_region)

        return service_regions

    @classmethod
    def generate_region_from_service_lookup(cls, service_region_name: str):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "service_region_info.json")

        with open(file_path) as regions_data:
            regions = json.load(regions_data)

        service_region_info = regions[service_region_name]

        return cls(service_region_info["sb_region"])