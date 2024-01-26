
# How to Run

```bash
python -m uvicorn main:app --reload
```

## API Reference

#### Post an expression to evaluate

```http
  POST /evaluate
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `expression` | `string` | **Required** |

#### Get CSV file 

```http
  GET /download
```
