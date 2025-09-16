<div align="center">
  
# LAMBDA - LArge Model-based Data Analysis System
[![Docs](https://img.shields.io/badge/Docs-Online-blue)](https://ama-cmfai.github.io/LAMBDA-Docs/#/)
[![Project](https://img.shields.io/badge/Project-Webpage-brightgreen)](https://www.polyu.edu.hk/ama/cmfai/lambda.html)
[![Paper](https://img.shields.io/badge/Paper-arXiv-red)](https://arxiv.org/pdf/2407.17535)
[![MacOS](https://img.shields.io/badge/Download-macOS-black?logo=apple)](https://github.com/AMA-CMFAI/LAMBDA/releases/download/app/LAMBDA-MacOS-beta-v0.0.2.zip)
[![Windows](https://img.shields.io/badge/Download-Windows-blue?logo=windows)](https://github.com/AMA-CMFAI/LAMBDA/releases/download/app/LAMBDA-Windows-beta-v0.0.2.zip)

</div>

<body>
<!-- <img src="https://github.com/user-attachments/assets/df454158-79e4-4da4-ae03-eb687fe02f16" style="width: 80%"> -->
<!-- <p align="center">
  <img src="https://github.com/user-attachments/assets/6f6d49ef-40b7-46f2-88ae-b8f6d9719c3a" style="width: 600px;">
  ![lambda_mix](https://github.com/user-attachments/assets/db5574aa-9441-4c9d-b44d-3b225d11e0cc)
</p> -->
  
![LAMBDA_mix_250710](https://github.com/user-attachments/assets/5cdc113b-7d26-4328-8911-d421081f98ce)


We introduce **LAMBDA**, a novel open-source, code-free multi-agent data analysis system that harnesses the power of large models. LAMBDA is designed to address data analysis challenges in complex data-driven applications through the use of innovatively designed data agents that operate iteratively and generatively using natural language.

## News
- LAMBDA App for macOS and Windows has been released. Details can be found in [Released](https://github.com/AMA-CMFAI/LAMBDA/releases/tag/app). (Hint: There are some problems with the kernel installation in the APP. You should run `ipython kernel install --name lambda --user` to install the kernel in advance.)
- [Docs site](https://ama-cmfai.github.io/LAMBDA-Docs/#/) is available!

## Key Features

- **Code-Free Data Analysis**: Perform complex data analysis tasks through human language instruction.
- **Multi-Agent System**: Utilizes two key agent roles, the programmer and the inspector, to generate and debug code seamlessly.
- **User Interface**: This includes a robust user interface that allows direct user intervention in the operational loop.
- **Model Integration**: Flexibly integrates external models and algorithms to cater to customized data analysis needs.
- **Automatic Report Generation**: Concentrate on high-value tasks, rather than spending time and resources on report writing and formatting.
- **Jupyter Notebook Exporting**: Export the code and the results to Jupyter Notebook for reproduction and further analysis flexibly.

## Getting Started
### Installation
First, clone the repository.

```bash
git clone https://github.com/AMA-CMFAI/LAMBDA.git
cd LAMBDA
```

Then, we recommend creating a [Conda](https://docs.conda.io/en/latest/) environment for this project and installing the dependencies by following the commands:
```bash
conda create -n lambda python=3.10
conda activate lambda
```

Then, install the required packages:
```bash
pip install -r requirements.txt
```

Next, you should install the Jupyter kernel to create a local Code Interpreter:
```bash
ipython kernel install --name lambda --user
```

### Configuration to Easy Start
1. To use the Large Language Models, you should have an API key from [OpenAI](https://openai.com/api/pricing/) or other companies. Besides, we support OpenAI-Style interface for your local LLMs once deployed, available frameworks such as [Ollama](https://ollama.com/), [LiteLLM](https://docs.litellm.ai/docs/), [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory).
> Here are some products that offer free APIkeys for your reference: [OpenRouter](https://openrouter.ai/) and [SILICONFLOW](https://siliconflow.cn/)
2. Set your API key, models and working path in the config.yaml:
```bash
#================================================================================================
#                                       Config of the LLMs
#================================================================================================
conv_model : "gpt-4.1-mini" # Choose the model you want to use. We highly recommned using the advanced model.
programmer_model : "gpt-4.1-mini" 
inspector_model : "gpt-4.1-mini"
api_key : "sk-xxxxxxx" # The API Keys you buy.
base_url_conv_model : 'https://api.openai.com/v1' # The base url from the provider.
base_url_programmer : 'https://api.openai.com/v1'
base_url_inspector : 'https://api.openai.com/v1'


#================================================================================================
#                                       Config of the system
#================================================================================================
streaming : True
project_cache_path : "cache/conv_cache/" # Local cache path
max_attempts : 5 # The max attempts of self-correcting
max_exe_time: 18000 # The maximum time for the execution

#knowledge integration
retrieval : False # Whether to start a knowledge retrieval. If you don't create your knowledge base, you should set it to False
```


Finally, run the following command to start the LAMBDA with GUI:
```bash
python lambda_app.py
```


## Demonstration Videos

The performance of LAMBDA in solving data science problems is demonstrated in several case studies, including:
- **[Data Analysis](https://www.polyu.edu.hk/ama/cmfai/files/lambda/lambda.mp4)**
- **[Integrating Human Intelligence](https://www.polyu.edu.hk/ama/cmfai/files/lambda/knw.mp4)**
- **[Education](https://www.polyu.edu.hk/ama/cmfai/files/lambda/LAMBDA_education.mp4)**


## Planning Works
- [ ] Create a Logger for log.
- [ ] Pre-installation of popular packages in the kernel.
- [ ] Replace Gradio UI with OpenWebUI.
- [ ] Refactor the Knowledge Integration and Knowledge base module by ChromaDB.
- [ ] Add a Docker image for easier use.
- [x] Docsite.


## Updating History
See [Docs site](https://ama-cmfai.github.io/LAMBDA-Docs/#/).


## Related Works
If you are interested in Data Agent, you can take a look at :
- Our survey paper [[A Survey on Large Language Model-based Agents for Statistics and Data Science]](https://www.arxiv.org/pdf/2412.14222)
- and a reading list: [[Paper List of LLM-based Data Science Agents]](https://github.com/Stephen-SMJ/Reading-List-of-Large-Language-Model-Based-Data-Science-Agent)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



## Acknowledgements

Thank the contributors and the communities for their support and feedback.

---

> If you find our work useful in your research, consider citing our paper by:



```bash
@article{sun2024lambda,
        author = {Maojun Sun and Ruijian Han and Binyan Jiang and Houduo Qi and Defeng Sun and Yancheng Yuan and Jian Huang and},
        title = {LAMBDA: A Large Model Based Data Agent},
        journal = {Journal of the American Statistical Association},
        volume = {0},
        number = {ja},
        pages = {1--20},
        year = {2025},
        publisher = {ASA Website},
        doi = {10.1080/01621459.2025.2510000},
        URL = {https://doi.org/10.1080/01621459.2025.2510000},
        eprint = {https://doi.org/10.1080/01621459.2025.2510000}

}

@article{sun2024survey,
  title={A Survey on Large Language Model-based Agents for Statistics and Data Science},
  author={Sun, Maojun and Han, Ruijian and Jiang, Binyan and Qi, Houduo and Sun, Defeng and Yuan, Yancheng and Huang, Jian},
  journal={arXiv preprint arXiv:2412.14222},
  year={2024}
}
```
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AMA-CMFAI/LAMBDA&type=Date)](https://www.star-history.com/#AMA-CMFAI/LAMBDA&Date)
</body>
