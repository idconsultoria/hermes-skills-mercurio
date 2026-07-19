# Erro 428 no Baileys — Diagnóstico e Correção

## Sintoma

```
connected to WA                          ← WebSocket abre normalmente
not logged in, attempting registration...
📱 QR Code gerado                        ← QR aparece
⚠️ Conexão fechada (code: 428)          ← WhatsApp MATA a conexão
🔄 Tentativa 1/10 em 3s...              ← reconecta, novo QR, ciclo repete
```

O usuário vê "não foi possível conectar" no celular após escanear. O servidor fica em loop de QR → 428 → reconexão → QR.

## Causas (3 fatores, por ordem de probabilidade)

### 1. Browser UA string rejeitada (PRINCIPAL)

O `makeWASocket` sem parâmetro `browser` usa default `["Ubuntu", "Chrome", "22.04.4"]`. O WhatsApp passou a rejeitar UA strings de Linux/datacenter em pareamentos novos.

**Fontes:**
- [Issue #1382](https://github.com/WhiskeySockets/Baileys/issues/1382) — `requestPairingCode` também quebra com 428, corrigido com browser Windows
- [Issue #2008](https://github.com/WhiskeySockets/Baileys/issues/2008) — confirma que `browser: ["Windows", "Chrome", "114.0.5735.198"]` resolve

**Correção:**
```js
browser: ["Windows", "Chrome", "114.0.5735.198"]
```

### 2. IP de datacenter (Oracle Cloud)

WhatsApp intensificou bloqueio de IPs de cloud providers conhecidos. O WebSocket abre (handshake TCP), mas o pareamento é derrubado. Sessões já estabelecidas (como `assessor1`) continuam funcionando — novos pareamentos sofrem mais escrutínio.

### 3. `defaultQueryTimeoutMs` não definido como `undefined`

[Issue #390](https://github.com/WhiskeySockets/Baileys/issues/390) documenta que em ambientes cloud, o timeout padrão pode matar a conexão durante o handshake de pareamento.

**Correção:**
```js
defaultQueryTimeoutMs: undefined
```

## Configuração completa corrigida

```js
const sock = makeWASocket({
    auth: state,
    version,
    browser: ["Windows", "Chrome", "114.0.5735.198"],  // ← CORREÇÃO 1
    defaultQueryTimeoutMs: undefined,                     // ← CORREÇÃO 2
    connectTimeoutMs: 60_000,
    qrTimeout: 60_000,
});
```

## Fallback: Pairing Code

Se o QR continuar falhando mesmo com as correções acima, use `requestPairingCode(phoneNumber)`:

```js
const code = await sock.requestPairingCode("5579984233338");
// → "TA65-DJMT"
```

O usuário digita esse código no WhatsApp (Dispositivos Conectados → Vincular com número de telefone). A autenticação é a mesma — o `creds.json` resultante é idêntico ao do fluxo QR.

**Pré-requisito:** o número passado para `requestPairingCode` deve ser o número de WhatsApp do usuário em formato E.164 sem `+` (ex: `5579984233338`).

## Sessão de exemplo (Oracle Cloud, Jul 2026)

- **Baileys:** 6.7.23
- **Servidor:** Oracle ARM (2 vCPU, 12 GB)
- **Sessão existente (assessor1):** conecta normalmente (~2s)
- **Sessão nova (avulso1):** 428 em loop — UA string Linux + datacenter IP
- **Correção aplicada:** browser Windows + `defaultQueryTimeoutMs: undefined`
