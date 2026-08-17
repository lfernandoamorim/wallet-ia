O revisor encontrou problemas na sua implementação da Task 4. Por favor, aplique as seguintes correções:

### Important (Should Fix)
- `tests/domains/users/test_directive.py`: `app.dependency_overrides[get_session] = override_get_session` foi definido no escopo global do módulo sem limpeza após o teste. Causa poluição de estado global no FastAPI, fazendo com que testes subsequentes herdem o mock de sessão indevidamente. Encapsule o override em uma fixture pytest com `yield` e execute `app.dependency_overrides.clear()` no teardown.
- `app/domains/users/orchestration.py`: Presença de comentários em inglês (`# Minimal implementation for MVP` e `# Mock hash for now`). Isso viola a regra global obrigatória do projeto de manter todo código e comentários em português (`pt-br`). Traduza ou substitua os comentários por docstrings em português.

### Minor (Nice to Have)
- `app/domains/users/directive.py`: O decorador `@router.post("/", response_model=UserResponse)` não especifica `status_code=status.HTTP_201_CREATED`. Adicione `status_code=201`.
- `app/domains/users/directive.py`, `app/domains/users/orchestration.py`, `app/main.py`: Ausência de docstrings nos módulos e funções. Inclua docstrings padronizadas em pt-br descrevendo responsabilidades e tipos.
- `app/domains/users/orchestration.py`: O parâmetro `user_data: dict` possui tipagem genérica. Utilize um TypedDict (ex: `class UserData(TypedDict):`) ou `dict[str, Any]` se for mais adequado, para garantir validação e clareza.
