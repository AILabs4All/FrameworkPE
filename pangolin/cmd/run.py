from pangolin.core.project.pangolin_project import PangolinProject
from pangolin.core.framework import PangolinFramework
from pangolin.core.observability.logger import setup_logger
from dotenv import load_dotenv


def run_command(
    columns=None,
    model=None,
    technique=None,
    output=None,
    max_iterations=None,
    temperature=None,
    max_tokens=None,
    verbose=False,
):
    """Executa o comando run (lógica desacoplada do CLI)"""

    def verify_project_directory():
        try:
            project = PangolinProject.load_from_current_dir()
            if project is None:
                logger = setup_logger("pg-run")
                logger.info("Erro: Voce nao esta em um diretorio de projeto Pangolin")
                return None
            return project
        except Exception as e:
            logger = setup_logger("pg-run")
            logger.info(f"Erro ao verificar projeto: {e}")
            return None

    project = verify_project_directory()
    if project is None:
        return 1

    load_dotenv(project.env_path, override=False)

    logger = setup_logger("pg-run", log_dir=str(project.logs_dir))
    logger.info(f"Executando projeto '{project.project_name}'")

    try:
        data_files = list(project.data_dir.glob("*"))
        if not data_files:
            logger.info("Nenhum arquivo em data/")
            return 1

        config = project.load_config()

        columns = columns or config.get('data', {}).get('input_columns', [])
        models_config = config.get('models', [])
        
        selected_models = []
        if model:
            # If user specified a model, try to find its config by name
            for m in models_config:
                if m.get('name') == model:
                    selected_models.append(m)
                    break
            # If not found, fail with the list of available models (no silent default)
            if not selected_models:
                available = [m.get('name', '?') for m in models_config]
                raise ValueError(
                    f"Modelo '{model}' não encontrado no config.yaml."
                    f" Modelos disponíveis: {', '.join(available) or '(nenhum modelo configurado)'}"
                )
        else:
            selected_models = models_config

        technique = technique or config.get('prompt', {}).get('technique', [])
        if not isinstance(technique, list):
            technique = [technique]
            
        output = output or config.get('output', {}).get('format', 'csv')

        if not columns:
            logger.info("Colunas nao especificadas")
            return 1

        if not selected_models:
            logger.info("Modelo nao especificado")
            return 1

        if not technique:
            logger.info("Tecnica nao especificada")
            return 1

        framework = PangolinFramework(project=project)

        technique_params = {}
        if max_iterations is not None:
            technique_params['max_iterations'] = max_iterations
        if temperature is not None:
            technique_params['temperature'] = temperature
        if max_tokens is not None:
            technique_params['max_tokens'] = max_tokens

        print(f"\nRodando experimento")
        print(f"Modelos: {[m.get('name') for m in selected_models]}")
        print(f"Tecnicas: {technique}")
        print(f"Colunas: {columns}\n")
        
        all_results = []
        for model_config in selected_models:
            model_name = model_config.get('name')
            print(f"\nProcessando com modelo: {model_name}")
            
            results = framework.process_incidents(
                input_dir=str(project.data_dir),
                columns=columns,
                model_config=model_config,
                prompt_techniques=technique,
                output_format=output,
                **technique_params
            )
            all_results.append(results)

        print("\nConcluido")
        if all_results:
            output_files = [
                path
                for result in all_results
                for path in result.get("output_files", [])
            ]
            if output_files:
                print("Arquivos de saída:")
                for output_file in output_files:
                    print(f"  {output_file}")

        return 0

    except Exception as e:
        print(f"Erro: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1
