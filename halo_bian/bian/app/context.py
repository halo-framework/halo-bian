
from halo_app.app.context import HaloContext, InitCtxFactory


# Finance Context - Multi 10
class BianContext(HaloContext):
    COMPANY = "Company"
    OPERATIONAL_ENTITY = "Operational Entity"
    BRAND = "Brand"
    CHANNEL = "Channel"
    ENVIRONMENT = "Environment"
    COUNTRY = "Country"
    TIME_ZONE = "Time Zone"
    LANGUAGE = "Language"
    BRANCH = "Branch"
    APP_CLIENT = "App Client"
    CONSUMER = "Consumer"
    BIZ_SCENARIO = "Biz Scenario"

    method = "method"

    HaloContext.items[COMPANY] = "x-bian-company"
    HaloContext.items[OPERATIONAL_ENTITY] = "x-bian-op-entity"
    HaloContext.items[BRAND] = "x-bian-brand"
    HaloContext.items[CHANNEL] = "x-bian-channel"
    HaloContext.items[ENVIRONMENT] = "x-bian-env"
    HaloContext.items[COUNTRY] = "x-bian-country"
    HaloContext.items[TIME_ZONE] = "x-bian-tz"
    HaloContext.items[LANGUAGE] = "x-bian-language"
    HaloContext.items[BRANCH] = "x-bian-branch"
    HaloContext.items[APP_CLIENT] = "x-bian-app-client"
    HaloContext.items[CONSUMER] = "x-bian-consumer"
    HaloContext.items[BIZ_SCENARIO] = "x-bian-biz-scenario"


class BianCtxFactory(InitCtxFactory):

    def get_initial_context(env:dict)->HaloContext:
        return BianContext(env)

