# DSL Templates

Three complete, import-ready DSL templates demonstrating common patterns. All use `version: "0.6.0"`.

## 1. Minimal Chatflow

`start → llm → answer`. Simplest working advanced-chat DSL. Good format anchor.

```yaml
app:
  description: ''
  icon: 🤖
  icon_background: '#FFEAD5'
  icon_type: emoji
  mode: advanced-chat
  name: Minimal Chatflow
  use_icon_as_answer_icon: false
kind: app
version: "0.6.0"
dependencies: []
workflow:
  conversation_variables: []
  environment_variables: []
  features:
    file_upload:
      allowed_file_extensions: []
      allowed_file_types: []
      allowed_file_upload_methods: []
      enabled: false
      fileUploadConfig:
        audio_file_size_limit: 50
        batch_count_limit: 5
        file_size_limit: 15
        image_file_size_limit: 10
        video_file_size_limit: 100
        workflow_file_upload_limit: 10
      image:
        enabled: false
        number_limits: 3
        transfer_methods: []
      number_limits: 3
    opening_statement: ''
    retriever_resource:
      enabled: true
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
      language: ''
      voice: ''
  graph:
    nodes:
      - id: '1000001'
        type: custom
        height: 72
        width: 242
        position: { x: 0, y: 282 }
        positionAbsolute: { x: 0, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          selected: false
          title: 用户输入
          type: start
          variables: []
      - id: '1000002'
        type: custom
        height: 87
        width: 242
        position: { x: 342, y: 282 }
        positionAbsolute: { x: 342, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          context:
            enabled: false
            variable_selector: []
          model:
            completion_params:
              temperature: 0.7
            mode: chat
            name: gpt-4o
            provider: langgenius/openai/openai
          prompt_template:
            - id: '1'
              role: system
              text: 'You are a helpful assistant.'
            - id: '2'
              role: user
              text: '{{#1000001.sys.query#}}'
          selected: false
          title: LLM
          type: llm
          vision:
            enabled: false
      - id: '1000003'
        type: custom
        height: 103
        width: 242
        position: { x: 684, y: 282 }
        positionAbsolute: { x: 684, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          answer: '{{#1000002.text#}}'
          selected: false
          title: 回复
          type: answer
          variables: []
    edges:
      - id: 1000001-source-1000002-target
        source: '1000001'
        sourceHandle: source
        target: '1000002'
        targetHandle: target
        type: custom
        zIndex: 0
        selected: false
        data:
          isInIteration: false
          isInLoop: false
          sourceType: start
          targetType: llm
      - id: 1000002-source-1000003-target
        source: '1000002'
        sourceHandle: source
        target: '1000003'
        targetHandle: target
        type: custom
        zIndex: 0
        selected: false
        data:
          isInIteration: false
          isInLoop: false
          sourceType: llm
          targetType: answer
    viewport:
      x: 0
      y: 0
      zoom: 1
```

## 2. Loop Orchestration

`start → loop(router → agents → assigners) → answer`. Multi-agent loop with LLM router and if-else phase dispatch.

```yaml
app:
  description: 'Multi-agent loop orchestration'
  icon: 🔄
  icon_background: '#E4FBCC'
  icon_type: emoji
  mode: advanced-chat
  name: Loop Orchestration
  use_icon_as_answer_icon: false
kind: app
version: "0.6.0"
dependencies: []
workflow:
  conversation_variables:
    - id: 'd4e1f2a3-b4c5-46d7-8e9f-0a1b2c3d4e5f'
      name: phase
      description: 当前阶段
      selector: [conversation, phase]
      value_type: string
      value: ''
    - id: 'a1b2c3d4-e5f6-4789-abcd-ef0123456789'
      name: round_count
      description: 轮次计数
      selector: [conversation, round_count]
      value_type: integer
      value: 0
  environment_variables: []
  features:
    file_upload:
      allowed_file_extensions: []
      allowed_file_types: []
      allowed_file_upload_methods: []
      enabled: false
      fileUploadConfig:
        audio_file_size_limit: 50
        batch_count_limit: 5
        file_size_limit: 15
        image_file_size_limit: 10
        video_file_size_limit: 100
        workflow_file_upload_limit: 10
      image:
        enabled: false
        number_limits: 3
        transfer_methods: []
      number_limits: 3
    opening_statement: ''
    retriever_resource:
      enabled: true
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
      language: ''
      voice: ''
  graph:
    nodes:
      # start
      - id: '1780164189283'
        type: custom
        height: 72
        width: 242
        position: { x: 0, y: 282 }
        positionAbsolute: { x: 0, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          selected: false
          title: 用户输入
          type: start
          variables: []
      # loop
      - id: '1780164194792'
        type: custom
        height: 600
        width: 1400
        position: { x: 342, y: 0 }
        positionAbsolute: { x: 342, y: 0 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          break_conditions: []
          error_handle_mode: terminated
          logical_operator: and
          loop_count: 10
          selected: false
          start_node_id: 1780164194792start
          title: 主循环
          type: loop
        zIndex: 1
      # loop-start
      - id: 1780164194792start
        type: custom-loop-start
        height: 48
        width: 44
        position: { x: 20, y: 300 }
        positionAbsolute: { x: 362, y: 300 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        draggable: false
        selectable: false
        data:
          desc: ''
          isInLoop: true
          selected: false
          title: ''
          type: loop-start
        zIndex: 1002
      # llm router (inside loop)
      - id: '1780164339362'
        type: custom
        height: 87
        width: 242
        position: { x: 80, y: 280 }
        positionAbsolute: { x: 422, y: 280 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        selected: false
        data:
          context:
            enabled: false
            variable_selector: []
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          model:
            completion_params:
              temperature: 0
            mode: chat
            name: gpt-4o
            provider: langgenius/openai/openai
          prompt_template:
            - id: '1'
              role: system
              text: |
                你是任务路由器。根据当前阶段决定下一步。

                规则：
                1. phase为空 → 首次，输出 NEXT_PHASE: agent_a
                2. phase=agent_a_done → NEXT_PHASE: agent_b
                3. phase=agent_b_done → NEXT_PHASE: done

                输出格式: NEXT_PHASE: [agent_a|agent_b|done]
            - id: '2'
              role: user
              text: |
                当前阶段: {{#conversation.phase#}}
                轮次: {{#conversation.round_count#}}
          selected: false
          title: 路由器
          type: llm
          vision:
            enabled: false
        zIndex: 1002
      # if-else dispatch (inside loop)
      - id: '1780164346416'
        type: custom
        height: 120
        width: 242
        position: { x: 400, y: 280 }
        positionAbsolute: { x: 742, y: 280 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        selected: false
        data:
          cases:
            - case_id: agent_a
              conditions:
                - comparison_operator: contains
                  id: cond-a
                  value: 'NEXT_PHASE: agent_a'
                  varType: string
                  variable_selector: ['1780164339362', text]
              id: agent_a
              logical_operator: and
            - case_id: agent_b
              conditions:
                - comparison_operator: contains
                  id: cond-b
                  value: 'NEXT_PHASE: agent_b'
                  varType: string
                  variable_selector: ['1780164339362', text]
              id: agent_b
              logical_operator: and
            - case_id: done
              conditions:
                - comparison_operator: contains
                  id: cond-done
                  value: 'NEXT_PHASE: done'
                  varType: string
                  variable_selector: ['1780164339362', text]
              id: done
              logical_operator: and
          desc: ''
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          selected: false
          title: 路由分发
          type: if-else
        zIndex: 1002
      # agent_a (inside loop)
      - id: '1780164383571'
        type: custom
        height: 79
        width: 242
        position: { x: 720, y: 100 }
        positionAbsolute: { x: 1062, y: 100 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        selected: false
        data:
          agent_parameters:
            instruction:
              type: constant
              value: 'You are Agent A. Complete your task and output results.'
            model:
              type: constant
              value:
                completion_params: {}
                mode: chat
                model: gpt-4o
                model_type: llm
                provider: langgenius/openai/openai
                type: model-selector
            query:
              type: constant
              value: '{{#sys.query#}}'
            tools:
              type: constant
              value: []
          agent_strategy_label: ReAct
          agent_strategy_name: ReAct
          agent_strategy_provider_name: langgenius/agent/agent
          desc: ''
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          output_schema: null
          plugin_unique_identifier: langgenius/agent:0.0.37@<hash>
          selected: false
          title: Agent A
          type: agent
        zIndex: 1002
      # assigner_a (inside loop) → sets phase=agent_a_done
      - id: '1780166088469'
        type: custom
        height: 90
        width: 242
        position: { x: 980, y: 100 }
        positionAbsolute: { x: 1322, y: 100 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        selected: false
        data:
          desc: ''
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          items:
            - input_type: variable
              operation: over-write
              value: ['1780164383571', text]
              variable_selector: [conversation, result_a]
              write_mode: over-write
            - input_type: constant
              operation: over-write
              value: agent_a_done
              variable_selector: [conversation, phase]
              write_mode: over-write
            - input_type: constant
              operation: +=
              value: '1'
              variable_selector: [conversation, round_count]
              write_mode: over-write
          selected: false
          title: 保存A→下一阶段
          type: assigner
          version: '2'
        zIndex: 1002
      # agent_b (inside loop) — same structure as agent_a
      - id: '1780164389952'
        type: custom
        height: 79
        width: 242
        position: { x: 720, y: 360 }
        positionAbsolute: { x: 1062, y: 360 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        selected: false
        data:
          agent_parameters:
            instruction:
              type: constant
              value: 'You are Agent B. Review Agent A output and produce final result.'
            model:
              type: constant
              value:
                completion_params: {}
                mode: chat
                model: gpt-4o
                model_type: llm
                provider: langgenius/openai/openai
                type: model-selector
            query:
              type: constant
              value: 'Agent A result: {{#conversation.result_a#}}'
            tools:
              type: constant
              value: []
          agent_strategy_label: ReAct
          agent_strategy_name: ReAct
          agent_strategy_provider_name: langgenius/agent/agent
          desc: ''
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          output_schema: null
          plugin_unique_identifier: langgenius/agent:0.0.37@<hash>
          selected: false
          title: Agent B
          type: agent
        zIndex: 1002
      # assigner_b (inside loop) → sets phase=agent_b_done
      - id: '1780166090810'
        type: custom
        height: 90
        width: 242
        position: { x: 980, y: 360 }
        positionAbsolute: { x: 1322, y: 360 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        selected: false
        data:
          desc: ''
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          items:
            - input_type: variable
              operation: over-write
              value: ['1780164389952', text]
              variable_selector: [conversation, result_b]
              write_mode: over-write
            - input_type: constant
              operation: over-write
              value: agent_b_done
              variable_selector: [conversation, phase]
              write_mode: over-write
            - input_type: constant
              operation: +=
              value: '1'
              variable_selector: [conversation, round_count]
              write_mode: over-write
          selected: false
          title: 保存B→下一阶段
          type: assigner
          version: '2'
        zIndex: 1002
      # reset assigner (inside loop) → phase="" triggers break
      - id: '1780165950328'
        type: custom
        height: 80
        width: 242
        position: { x: 720, y: 560 }
        positionAbsolute: { x: 1062, y: 560 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        selected: false
        data:
          desc: ''
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          items:
            - input_type: constant
              operation: over-write
              value: ''
              variable_selector: [conversation, phase]
              write_mode: over-write
            - input_type: constant
              operation: over-write
              value: '0'
              variable_selector: [conversation, round_count]
              write_mode: over-write
          selected: false
          title: 重置→退出循环
          type: assigner
          version: '2'
        zIndex: 1002
      # loop-end
      - id: '1780166166882'
        type: custom-simple
        height: 52
        width: 243
        position: { x: 980, y: 560 }
        positionAbsolute: { x: 1322, y: 560 }
        sourcePosition: right
        targetPosition: left
        parentId: '1780164194792'
        data:
          isInIteration: false
          isInLoop: true
          loop_id: '1780164194792'
          selected: false
          title: 退出循环
          type: loop-end
        zIndex: 1002
      # answer (outside loop)
      - id: '1780164239686'
        type: custom
        height: 103
        width: 242
        position: { x: 1852, y: 282 }
        positionAbsolute: { x: 1852, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          answer: |
            ## Agent A 结果
            {{#conversation.result_a#}}

            ## Agent B 结果
            {{#conversation.result_b#}}
          selected: false
          title: 最终输出
          type: answer
          variables: []
    edges:
      - id: 1780164189283-source-1780164194792-target
        source: '1780164189283'
        sourceHandle: source
        target: '1780164194792'
        targetHandle: target
        type: custom
        zIndex: 0
        selected: false
        data: { isInIteration: false, isInLoop: false, sourceType: start, targetType: loop }
      - id: 1780164194792-source-1780164239686-target
        source: '1780164194792'
        sourceHandle: source
        target: '1780164239686'
        targetHandle: target
        type: custom
        zIndex: 0
        selected: false
        data: { isInIteration: false, isInLoop: false, sourceType: loop, targetType: answer }
      - id: 1780164194792start-source-1780164339362-target
        source: 1780164194792start
        sourceHandle: source
        target: '1780164339362'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: loop-start, targetType: llm }
      - id: 1780164339362-source-1780164346416-target
        source: '1780164339362'
        sourceHandle: source
        target: '1780164346416'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: llm, targetType: if-else }
      - id: 1780164346416-agent_a-1780164383571-target
        source: '1780164346416'
        sourceHandle: agent_a
        target: '1780164383571'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: if-else, targetType: agent }
      - id: 1780164383571-source-1780166088469-target
        source: '1780164383571'
        sourceHandle: source
        target: '1780166088469'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: agent, targetType: assigner }
      - id: 1780166088469-source-1780166166882-target
        source: '1780166088469'
        sourceHandle: source
        target: '1780166166882'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: assigner, targetType: loop-end }
      - id: 1780164346416-agent_b-1780164389952-target
        source: '1780164346416'
        sourceHandle: agent_b
        target: '1780164389952'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: if-else, targetType: agent }
      - id: 1780164389952-source-1780166090810-target
        source: '1780164389952'
        sourceHandle: source
        target: '1780166090810'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: agent, targetType: assigner }
      - id: 1780166090810-source-1780166166882-target
        source: '1780166090810'
        sourceHandle: source
        target: '1780166166882'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: assigner, targetType: loop-end }
      - id: 1780164346416-done-1780165950328-target
        source: '1780164346416'
        sourceHandle: done
        target: '1780165950328'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: if-else, targetType: assigner }
      - id: 1780165950328-source-1780166166882-target
        source: '1780165950328'
        sourceHandle: source
        target: '1780166166882'
        targetHandle: target
        type: custom
        zIndex: 1002
        selected: false
        data: { isInIteration: false, isInLoop: true, loop_id: '1780164194792', sourceType: assigner, targetType: loop-end }
    viewport:
      x: 0
      y: 0
      zoom: 0.5
```

## 3. Trigger Schedule Workflow

`trigger-schedule → http-request → code → end`. Scheduled workflow that fetches data, processes it, and returns structured output. Workflow mode (not chatflow).

```yaml
app:
  description: 'Scheduled data fetch and processing'
  icon: ⏰
  icon_background: '#E4FBCC'
  icon_type: emoji
  mode: workflow
  name: Scheduled Workflow
  use_icon_as_answer_icon: false
kind: app
version: "0.6.0"
dependencies: []
workflow:
  conversation_variables: []
  environment_variables:
    - id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
      name: API_KEY
      value: ''
      description: ''
      selector: [env, API_KEY]
      value_type: string
  features:
    file_upload:
      allowed_file_extensions: []
      allowed_file_types: []
      allowed_file_upload_methods: []
      enabled: false
      fileUploadConfig:
        audio_file_size_limit: 50
        batch_count_limit: 5
        file_size_limit: 15
        image_file_size_limit: 10
        video_file_size_limit: 100
        workflow_file_upload_limit: 10
      image:
        enabled: false
        number_limits: 3
        transfer_methods: []
      number_limits: 3
    opening_statement: ''
    retriever_resource:
      enabled: true
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
      language: ''
      voice: ''
  graph:
    nodes:
      # trigger-schedule
      - id: '2000001'
        type: custom
        height: 72
        width: 242
        position: { x: 0, y: 282 }
        positionAbsolute: { x: 0, y: 282 }
        sourcePosition: right
        targetPosition: left
        data:
          cron_expression: '0 */6 * * *'
          desc: ''
          mode: cron
          selected: false
          timezone: Asia/Shanghai
          title: 每6小时
          type: trigger-schedule
      # http-request
      - id: '2000002'
        type: custom
        height: 106
        width: 242
        position: { x: 342, y: 282 }
        positionAbsolute: { x: 342, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          authorization:
            type: api-key
            config:
              api_key: '{{#env.API_KEY#}}'
              header: Authorization
              type: bearer
          body:
            type: none
          desc: ''
          headers: ''
          method: get
          params: ''
          retry_config:
            max_retries: 3
            retry_enabled: true
            retry_interval: 1000
          selected: false
          timeout:
            connect: 10
            max_connect_timeout: 0
            max_read_timeout: 0
            max_write_timeout: 0
            read: 60
            write: 60
          title: HTTP
          type: http-request
          url: 'https://api.example.com/data'
      # code
      - id: '2000003'
        type: custom
        height: 88
        width: 242
        position: { x: 684, y: 282 }
        positionAbsolute: { x: 684, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          code: |
            import json

            def main(http_body: str) -> dict:
                data = json.loads(http_body)
                items = data.get("items", [])
                count = len(items)
                return {
                    "count": count,
                    "items": items
                }
          code_language: python3
          desc: ''
          outputs:
            count:
              children: null
              type: number
            items:
              children: null
              type: array[object]
          selected: false
          title: Code
          type: code
          variables:
            - value_selector:
                - '2000002'
                - body
              variable: http_body
      # end
      - id: '2000004'
        type: custom
        height: 88
        width: 242
        position: { x: 1026, y: 282 }
        positionAbsolute: { x: 1026, y: 282 }
        sourcePosition: right
        targetPosition: left
        selected: false
        data:
          desc: ''
          outputs:
            - value_selector:
                - '2000003'
                - count
              variable: count
            - value_selector:
                - '2000003'
                - items
              variable: items
          selected: false
          title: 结束
          type: end
    edges:
      - id: 2000001-source-2000002-target
        source: '2000001'
        sourceHandle: source
        target: '2000002'
        targetHandle: target
        type: custom
        zIndex: 0
        selected: false
        data: { isInIteration: false, isInLoop: false, sourceType: trigger-schedule, targetType: http-request }
      - id: 2000002-source-2000003-target
        source: '2000002'
        sourceHandle: source
        target: '2000003'
        targetHandle: target
        type: custom
        zIndex: 0
        selected: false
        data: { isInIteration: false, isInLoop: false, sourceType: http-request, targetType: code }
      - id: 2000003-source-2000004-target
        source: '2000003'
        sourceHandle: source
        target: '2000004'
        targetHandle: target
        type: custom
        zIndex: 0
        selected: false
        data: { isInIteration: false, isInLoop: false, sourceType: code, targetType: end }
    viewport:
      x: 0
      y: 0
      zoom: 1
```
