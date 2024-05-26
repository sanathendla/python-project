'''
Function that train custom images from your
labeled repository

Author: Vitor Abdo
Date: June/2023
'''

# import necessary packages
import logging
import timeit
import sys
import os
import shutil
import torch
import wandb
from ultralytics import YOLO

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s')

# config
DATA = sys.argv[1]
EPOCHS = int(sys.argv[2])
BATCH = int(sys.argv[3])
MODEL_NAME = sys.argv[4]
LR0 = float(sys.argv[5])
LRF = float(sys.argv[6])
WEIGHT_DECAY = float(sys.argv[7])
BEST_MODEL_PATH = sys.argv[8]
RUNS_PATH = sys.argv[9]


def train_custom_yolo_model(
    data: str,
    epochs: int,
    batch: int,
    model_name: str,
    lr0: float,
    lrf: float,
    weight_decay: float) -> tuple:
    '''
    Function to train a custom model using YOLO v8.

    Args:
    - data (str): Data configuration file path. Default is 'data.yaml'.
    - epochs (int): Number of training epochs. Default is 20.
    - batch (int): Batch size. Default is 8.
    - augment (bool): Flag to enable data augmentation. Default is True.
    - model_name (str): Output model name. Default is 'yolov8n_drowsiness'.
    - lr0 (float): Initial learning rate for optimizer. Default is 0.01.
    - lrf (float): Final learning rate for optimizer. Default is 0.01.
    - weight_decay (float): Weight decay for optimizer. Default is 0.0005.

    Returns:
    - results (Tuple): A tuple containing the training results.
    '''
    # Load the pretrained model
    model = YOLO('yolov8n.pt')

    # Training settings
    logging.info('Starting training...')
    logging.info(f'Data configuration: {data}')
    logging.info(f'Epochs: {epochs}')
    logging.info(f'Batch size: {batch}')
    logging.info(f'Model name: {model_name}')
    logging.info(f'Initial learning rate: {lr0}')
    logging.info(f'Final learning rate: {lrf}')
    logging.info(f'Weight decay: {weight_decay}')

    # Train the model
    results = model.train(
        data=data,
        epochs=epochs,
        batch=batch,
        name=model_name,
        lr0=lr0,
        lrf=lrf,
        weight_decay=weight_decay,
    )

    logging.info('Training completed.')
    return results


if __name__ == "__main__":
    logging.info('About to start executing the train_data component\n')
    starttime = timeit.default_timer()

    # init run in wandb
    run = wandb.init(
        project='drowsiness_detection',
        entity='vitorabdo',
        job_type='Yolo train model')
    logging.info('Creating run for drowsiness detection: SUCCESS\n')

    # train the custom model
    os.environ['KMP_DUPLICATE_LIB_OK']='True'
    train_custom_yolo_model(DATA, EPOCHS, BATCH, MODEL_NAME, LR0, LRF, WEIGHT_DECAY)

    timing = timeit.default_timer() - starttime
    logging.info(f'The execution time of this step was:{timing}\n')

    # get the best model and upload in wandb
    weights_directory = BEST_MODEL_PATH

    artifact = wandb.Artifact(
        name='best_model_pipe',
        type='pt',
        description='Final model pipeline after training, exported in the correct format for making inferences'
        )
    artifact.add_file(weights_directory, name='best.pt')
    run.log_artifact(artifact)
    artifact.wait()
    run.finish()
    logging.info('Uploaded best model to wandb: SUCCESS\n')

    # remove the folder that are the best model
    shutil.rmtree(RUNS_PATH)
    logging.info('Runs folder deleted: SUCCESS\n')

    logging.info('Done executing the train_data component')
