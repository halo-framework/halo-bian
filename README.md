<p align="center">
  <img src="https://i.ibb.co/9V7gLNH/halo-plat.png" alt="Halo Serverless" border="0" height="250" width="500" />
</p>

# Halo Bian - Flask BIAN Python Reference Architecture Library

The **Halo Bian** library is based on the [**Halo**](https://github.com/yoramk2/halo_flask) library which is a python based library utilizing [**Serverless**](https://logz.io/blog/serverless-vs-containers/) technology and [**microservices architecture**](http://blog.binaris.com/your-guide-to-migrating-existing-microservices-to-serverless/) 


BIAN (Banking Industry Architecture Network) is a membership group committed to developing open standards around banking and financial services.  A key deliverable of this group is the BIAN Service Landscape model which defines a comprehensive services architecture for financial transactions and facilities.  This library is an implementation of the BIAN model leveraging the Flask framework and allows a developer to **rapidly create BIAN-compliant services** while hiding much of the underlying BIAN model details.  See www.bian.org for more information on BIAN.

This library leverages not only the Flask framework, but a number of the Flask Cloud Services components as well to facilitate building robust and resilient cloud-native BIAN microservices. 
deploy your Service Domain to your local environment or use [**Serverless Framework**](https://serverless.com/) and [**zappa**](https://github.com/Miserlou/Zappa) to deploy your Service Domain to AWS.

## BIAN Basics

Before diving into the library architecture, it helps to understand two key concepts within BIAN, service domains and control records.

### Service Domain

The BIAN Service Landscape defines discrete areas of responsibility known as service domains.  A **Service Domain** is a combination of a **Functional Pattern** and an **Asset Type**.  For instance, using the functional pattern 'Registry' with the asset type 'Product' would yield a 'Product Registry' service domain, which could be used to manage a product catalog.  If we instead changed the asset type to 'Device', we would have a 'Device Registry' service domain that could be used to authorize services on a mobile device.  

### Control Record

The **Control Record** is used to track the state of a service domain, and like the service domain is derived from the functional pattern and asset type.  However, in a control record, the functional pattern is represented by the **Generic Artifact Type**.  There is a one-to-one correlation between functional patterns and generic artifact types.  The control record goes one step further in delineating between specific service domain operations by introducing an additional parameter called the **Behavior Qualifier**, which, like generic artifact types, have a one-to-one correlation with functional patterns.

### In Addition

-  The commercial behaviors that are called Functional Patterns. Functional Patterns, Generic Artifacts and Behavior Qualifier Types are mapped and correlated:     
![Flask BIAN Functional Patterns](docs/internal_sd.png)<p/>
[**Image From Bian Manual**](https://bian.org)

-  A Service Domain applies one of the 18 functional patterns to instances of one type of asset:
![Flask BIAN Asset Types](docs/asset_types.png)<p/>
[**Image From Bian Manual**](https://bian.org)

-  The standard set of ‘action terms’ that characterize the range of service operation calls : 
![Flask BIAN Action Items](docs/action_items.png)<p/>
[**Image From Bian Manual**](https://bian.org)

-  The Default Action Term By Functional Pattern matrix:

![Flask BIAN Matrix](docs/matrix.png)<p/>
[**Image From Bian Manual**](https://bian.org)


### BIAN Summary

So to summarize the above:

**Functional Pattern** ==> **Generic Artifact Type** ==> **Behavior Qualifier**

**Functional Pattern** + **Asset Type** = **Service Domain**

**Generic Artifact Type** + **Asset Type** + (optional)**Behavior Qualifier** = **Control Record**

**Functional Pattern** is correlated with a set of **Action Term** = **Service Domain Operations**

Key Benefits of using BIAN API solutions:

-  Support for Emerging Industry Approaches – Two key technology approaches are considered: API development and the adoption of a Micro-service architecture
-  Support for Industry Standards – The BIAN Service Domains and service operations present an Industry standard definition for the componentization and service enablement of Banking
-  Support for Incremental Adoption/Migration – BIAN aligned solutions can be implemented and adopted incrementally enabling a prioritized migration from constraining legacy architectures

## Architecture

The Flask BIAN library implements a BIAN service domain wrapper that acts as an API and data translator while hiding much of the BIAN model complexity from the developer.

![Flask BIAN Service Domain](docs/Halo-BIANServiceDomain.png)

<p/>Halo Bian provides the following features:

-  Bian version 7 - API release competability
-  OAS ver. 2 support
-  BianRequest object provides bian parameters support
-  ServiceProperties object provides service status 
-  AssetType, GenericArtifact, BehaviorQualifier support per service domain
-  BianServiceInfo object privides Bian details per service
-  Support for all Bian Service Operations
-  Support for all FunctionalPatterns

<p/>Halo provides the following features:

-  Flask development for AWS Lambda & Dynamodb
-  [correlation id across microservices](https://theburningmonk.com/2017/09/capture-and-forward-correlation-ids-through-different-lambda-event-sources/)
-  [structured json based logging](https://theburningmonk.com/2018/01/you-need-to-use-structured-logging-with-aws-lambda/)
-  [sample debug log in production](https://theburningmonk.com/2018/04/you-need-to-sample-debug-logs-in-production/)
-  [support for microservice transactions with the saga pattern](https://read.acloud.guru/how-the-saga-pattern-manages-failures-with-aws-lambda-and-step-functions-bc8f7129f900)
-  [using SSM Parameter Store over Lambda env variables](https://hackernoon.com/you-should-use-ssm-parameter-store-over-lambda-env-variables-5197fc6ea45b)
-  [Serverless Error Handling & trace id for end users](https://aws.amazon.com/blogs/compute/error-handling-patterns-in-amazon-api-gateway-and-aws-lambda/)
-  [Lambda timeout](https://blog.epsagon.com/best-practices-for-aws-lambda-timeouts) management for [slow HTTP responses](https://theburningmonk.com/2018/01/aws-lambda-use-the-invocation-context-to-better-handle-slow-http-responses/)
-  [ootb support for Idempotent service invocations (md5)](https://cloudonaut.io/your-lambda-function-might-execute-twice-deal-with-it/)

If you are building a Python web app running on AWS Lambda (Flask), use this library to manage api transactions:

```
            sagax = load_saga("test", jsonx, schema)
            payloads = {"BookHotel": {"abc": "def"}, "BookFlight": {"abc": "def"}, "BookRental": {"abc": "def"},
                        "CancelHotel": {"abc": "def"}, "CancelFlight": {"abc": "def"}, "CancelRental": {"abc": "def"}}
            apis = {"BookHotel": self.create_api1, "BookFlight": self.create_api2, "BookRental": self.create_api3,
                    "CancelHotel": self.create_api4, "CancelFlight": self.create_api5, "CancelRental": self.create_api6}
            try:
                self.context = Util.get_lambda_context(request)
                ret = sagax.execute(self.req_context, payloads, apis)
                return {"saga": "good"}, 200
            except SagaRollBack as e:
                return {"saga": "bad"}, 500
```


## License

This project is licensed under the MIT License

## Acknowledgments

* Pivotal-Field-Engineering - https://github.com/Pivotal-Field-Engineering/spring-bian

* Bian api - https://github.com/bianapis

* Bian - http://bian.org


