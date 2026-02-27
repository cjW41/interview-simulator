# 核心 API
## 服务端
### 服务端异常

- `406`: 上传参数异常。
- `500`：服务端没有启动。


### job

岗位与岗位题库 API。

----
**GET_JOBS_LIST**

- Description: 获取当前服务端存储的岗位。
- Content-Type: `application/json`
- Method: `GET`
- Args:
	- `interview_ready` (*bool, defaults=`true`*) 
		是否仅查看可面试岗位。
- Response:
	- `jobs` (*array\[string]*)
		岗位列表。若无符合要求的岗位则返回空列表。

----
**GET_JOB_INFO**

- Description: 获取一个岗位的信息。
- Content-Type: `application/json`
- Method: `GET`
- Args:
	- `job_name` (*string*)
		岗位名称。
- Response:
	- `job_responsibility` (*string*)
		岗位职责。
	- `job_requirement` (*string*)
		岗位要求。
	- `question_banks` (*array\[string]*)
		面试涉及题库名称。
- Error:
	- `404`: 岗位不存在。

----
**CREATE_JOB**

- Description: 创建岗位。岗位以名称为唯一标识符。当岗位已存在时覆盖旧岗位。
- Content-Type: `multipart/form-data`
- Method: `PUT`
- Args: 
	- `job_name` (*string*)
		岗位名称（唯一标识符）。
	- `job_responsibility` (*string*)
		岗位职责。
	- `job_requirement` (*string*)
		岗位要求。
	- `question_banks` (*array\[string]*)
		面试涉及题库名称。
- Response: none	

----
**GET_QUESTION_BANKS_STATUS**

- Description: 查看所有领域题库状态。
- Content-Type: `application/json`
- Method: `GET`
- Args: none
- Response:
	- `status` (*array\[object]*)
		题库状态表。
		- `domain` (*string*)
			题库领域名称。
		- `complete` (*bool*)
			题库是否已经生成完毕。
		- `size` (*int*)
			已生成题目数量。
		- `total_size` (*int*)
			目标生成题目数量。
		- `sub_domains` (*array\[string]*)
			题库中的子领域名称。
		- `sub_domains_number` (*array*)
			题库中各子领域题目数量。

----
**CREATE_QUESTION_BANK**

- Description: 创建领域题库。
- Content-Type: `application/json`
- Method: `PUT`
- Args:
	- `name` (*string*)
		题库名称。
	- `domain` (*string*)
		题库所属领域名称。
	- `total_question_num` (*integer*)
		总题目数。
	- `sub_domain_ratio` (*array\[object]*)
		子领域题目比例。
		- `sub_domain_name` (*string*)
			子领域名称。
		- `ratio` (*float*)
			占比。(自动归一化)
- Response: none

----
**GET_QUESTION**

- Description: 从领域题库抽取问题。
- Content-Type: `application/json`
- Method: `GET`
- Args:
	- `domain` (*string*)
		领域名称。
	- `sub_domain` (*string*)
		子领域名称。
- Response:
	- `question` (*string*)
		题干。
	- `answer` (*string*)
		参考回答。
	- `scoring_criteria` (*string*)
		评分细则。


### agent

面试官管理 API。智能体无需通过 API 配置和管理，直接在源码上修改。

----
**GET_INTERVIEWERS**

- Description: 获取当前全部面试官的信息。
- Content-Type: `application/json`
- Method: `GET`
- Args: none
- Response:
	- `info` (*array\[object]*)
		- `name` (*string*)
			面试官名称。
		- `character_prompt` (*string*)
			角色提示词。
		- `model` (*string*)
			面试官所用模型名称。

----
**CREATE_INTERVIEWER**

- Description: 创建面试官。
- Content-Type: `application/json`
- Method: `PUT`
- Args:
	- `name` (*string*)
		面试官名称。
	- `character_prompt` (*string*)
		角色提示词。
	- `model` (*string*)
		面试官所用模型名称。
- Response: none

----
**GET_MODELS_LIST**

- Description: 查看所有模型状态
- Content-Type: `application/json`
- Method: `GET`
- Args: none
- Response:
	- `models` (*array\[object]*)
		模型状态列表。
		- `name` (*string*)
			模型名称
		- `is_local` (*bool*)
			是否是本地模型
		- `cost` (*int*)
			已使用大模型 API 费用（人工计算或从官方 API 查询）。
		- `think` (*bool*)
			是否支持思考模式。
		- `tool` (*bool*)
			是否支持工具调用。
		
- Error

- Description
- Content-Type: `application/json`
- Method
- Args
- Response
- Error


- Description
- Content-Type: `application/json`
- Method
- Args
- Response
- Error



- Description
- Content-Type: `application/json`
- Method
- Args
- Response
- Error


- Description
- Content-Type: `application/json`
- Method
- Args
- Response
- Error


- Description
- Content-Type: `application/json`
- Method
- Args
- Response
- Error