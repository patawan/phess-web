#!/usr/bin/env python3
import os

import aws_cdk as cdk

from phess_web.phess_web_stack import PhessWebStack


app = cdk.App()
PhessWebStack(scope=app,
              construct_id="PhessWebStack",
              env=cdk.Environment(
                  account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                  region=os.getenv('CDK_DEFAULT_REGION')
                  )
              )

app.synth()
