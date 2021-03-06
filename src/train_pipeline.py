import os
import logging.config
from typing import Dict

from omegaconf import DictConfig
import pandas as pd
import hydra

from src.data import split_train_val_data
from src.entities.train_pipeline_params import TrainingPipelineParams, TrainingPipelineParamsSchema
from src.features.build_features import get_target, build_transformer, prepare_dataset
from src.models import train_model, make_prediction, evaluate_model
from src.utils import read_data, save_pkl_file, save_metrics_to_json

logger = logging.getLogger("train_pipeline")


def train_pipeline(
        training_pipeline_params: TrainingPipelineParams,
) -> Dict[str, float]:
    logger.info(f"Start train pipeline with params {training_pipeline_params}")
    logger.info(f"Model is {training_pipeline_params.train_params.model_type}")

    data = read_data(training_pipeline_params.path_config.input_data_path)

    train_df, test_df = split_train_val_data(data, training_pipeline_params.splitting_params)
    #logger.info("Start transformer building...")
    #transformer = build_transformer(training_pipeline_params.feature_params)

    #transformer.fit(train_df)
    #save_pkl_file(transformer, training_pipeline_params.path_config.output_transformer_path)

    #train_features = pd.DataFrame(transformer.transform(train_df))

    train_target = get_target(train_df, training_pipeline_params.feature_params)
    #TODO передавать актуальные параметры
    train_df = prepare_dataset(train_df, training_pipeline_params.feature_params)


    logger.info("Start model training..")
    print(train_df.shape, train_target.shape)

    model = train_model(
        train_df, train_target, training_pipeline_params.train_params
    )
    logger.info("Model training is done")

    #test_features = pd.DataFrame(transformer.transform(test_df))

    test_target = get_target(test_df, training_pipeline_params.feature_params)
    #TODO передавать актуальные параметры
    test_df = prepare_dataset(test_df, training_pipeline_params.feature_params)


    predicts = make_prediction(model, test_df)

    metrics = evaluate_model(predicts, test_target)

    save_metrics_to_json(training_pipeline_params.path_config.metric_path,
                         metrics)

    logger.info("Model is saved")
    logger.info(f"Metrics for test dataset is {metrics}")

    save_pkl_file(model, training_pipeline_params.path_config.output_model_path)

    return metrics


@hydra.main(config_path="../configs", config_name="train_config")
def train_pipeline_start(cfg: DictConfig):
    os.chdir(hydra.utils.to_absolute_path(".."))
    schema = TrainingPipelineParamsSchema()
    params = schema.load(cfg)
    train_pipeline(params)


if __name__ == "__main__":
    train_pipeline_start()
