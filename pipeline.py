from sagemaker.workflow.pipeline import Pipeline
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.workflow.steps import ProcessingStep, ConditionStep
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import JsonGet
from sagemaker.workflow.properties import PropertyFile

# Step 1: Define the processor
script_processor = ScriptProcessor(
    image_uri='your-custom-image-uri',  # Or use built-in e.g. scikit-learn image
    command=['python3'],
    instance_type='ml.m5.large',
    instance_count=1,
    base_job_name='detect-impostors',
    role='your-sagemaker-execution-role'
)

# Step 2: PropertyFile to expose output metrics
impostor_prop = PropertyFile(
    name='ImpostorMetrics',
    output_name='output',
    path='impostor_count.json'
)

# Step 3: Processing Step
processing_step = ProcessingStep(
    name='DetectImpostorsStep',
    processor=script_processor,
    inputs=[
        ProcessingInput(source='s3://your-bucket/crew_data.csv',
                        destination='/opt/ml/processing/input/crew_data.csv')
    ],
    outputs=[
        ProcessingOutput(source='/opt/ml/processing/output',
                         destination='s3://your-bucket/output/')
    ],
    code='detect_impostors.py',
    property_files=[impostor_prop]
)

# Step 4: Condition Step
from sagemaker.workflow.steps import CreateModelStep  # not needed, just showing syntax
from sagemaker.processing import ProcessingOutputConfig

# Dummy processing steps (just simulate a branch outcome)
from sagemaker.workflow.steps import ProcessingStep

# "Impostor Detected" Step
alert_step = ProcessingStep(
    name="AlertStep",
    processor=script_processor,
    inputs=[],
    outputs=[
        ProcessingOutput(source="/opt/ml/processing/output",
                         destination='s3://your-bucket/branch-output/')
    ],
    code="""
with open("/opt/ml/processing/output/alert.txt", "w") as f:
    f.write("WARNING: Impostors detected on board!")
"""
)

# "Clean Crew" Step
celebrate_step = ProcessingStep(
    name="CelebrateStep",
    processor=script_processor,
    inputs=[],
    outputs=[
        ProcessingOutput(source="/opt/ml/processing/output",
                         destination='s3://your-bucket/branch-output/')
    ],
    code="""
with open("/opt/ml/processing/output/all_good.txt", "w") as f:
    f.write("No impostors found. All clear!")
"""
)

# Condition Step to branch
condition_step = ConditionStep(
    name="ImpostorCheckStep",
    conditions=[
        ConditionGreaterThanOrEqualTo(
            left=JsonGet(
                step_name=processing_step.name,
                property_file=impostor_prop,
                json_path="impostor_count"
            ),
            value=1
        )
    ],
    if_steps=[alert_step],
    else_steps=[celebrate_step]
)

# Build pipeline
pipeline = Pipeline(
    name="DetectImpostorsPipeline",
    steps=[processing_step, condition_step],
    sagemaker_session=sagemaker_session
)
