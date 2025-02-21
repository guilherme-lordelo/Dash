CREATE TABLE IF NOT EXISTS transactions (
    mes_referencia VARCHAR(6),
    estado_origem VARCHAR(2),
    codigo_ibge_municipio_origem INTEGER,
    estado_destino VARCHAR(2),
    codigo_ibge_municipio_destino INTEGER,
    cnae VARCHAR(7),
    descricao_cnae VARCHAR(255),
    ncm VARCHAR(8),
    cfop INTEGER,
    total_bruto NUMERIC(10, 2),
    icms NUMERIC(10, 2)
);
