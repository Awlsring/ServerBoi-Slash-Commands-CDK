import json
from typing import Set, Dict


class ServiceRegion(object):
    def __init__(self, name: str, location: str, service: str, emoji: str):
        self.name = name
        self.location = location
        self.service = service
        self.emoji = emoji

    def __repr__(self):
        return self.name


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
        with open("region_info.json") as regions_data:
            regions = json.load(regions_data)

        sb_region = regions[self.region_name]

        region_services = []
        for key in sb_region:

            region_services.append(key)

        print(sb_region)
        print(region_services)

        service_regions = {}
        for service in region_services:
            service_regions[service] = []
            for region in sb_region[service]:
                new_service_region = ServiceRegion(
                    region["name"], region["location"], service, region['emoji']
                )
                service_regions[service].append(new_service_region)

        return service_regions