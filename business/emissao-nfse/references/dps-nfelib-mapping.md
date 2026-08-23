# nfelib — binding NFS-e Nacional (DPS): árvore de classes/campos

Reverse-engineered em 18/08/2026 (nfelib 2.5.2) para montar a DPS do padrão
**NFS-e Nacional** sem redescobrir. Caminhos:

```
nfelib/nfse/bindings/v1_0/dps_v1_00.py          -> Dps, Tcdps
nfelib/nfse/bindings/v1_0/tipos_complexos_v1_00.py
nfelib/nfse/samples/v1_0/dps-regime-normal.xml   -> exemplo de referência
```

## Árvore (Dps raiz)

```
Dps(versao="1.00", infDPS=TcinfDps(...), signature=None)
└─ TcinfDps: tpAmb, dhEmi, verAplic, serie, nDPS, dCompet, tpEmit, cLocEmi,
             subst, prest, toma, interm, serv, valores, Id
   ├─ prest  = TcinfoPrestador(CNPJ, CPF, NIF, cNaoNIF, CAEPF, IM, xNome, end,
   │            fone, email, regTrib)
   │     regTrib = TcregTrib(opSimpNac, regApTribSN, regEspTrib)   # Simples Nac -> opSimpNac="2"
   ├─ toma   = TcinfoPessoa(CNPJ, CPF, NIF, cNaoNIF, CAEPF, IM, xNome, end, fone, email)
   │     end  = Tcendereco(endNac, endExt, xLgr, nro, xCpl, xBairro)
   │             endNac = TcenderNac(cMun, CEP)
   ├─ serv   = Tcserv(locPrest, cServ, comExt, lsadppu, obra, atvEvento, explRod, infoCompl)
   │     locPrest = TclocPrest(cLocPrestacao, cPaisPrestacao, opConsumServ)
   │     cServ    = Tccserv(cTribNac, cTribMun, xDescServ, cNBS, cIntContrib)
   └─ valores= TcinfoValores(vServPrest, vDescCondIncond, vDedRed, trib)
         vServPrest = TcvservPrest(vReceb, vServ)
         trib       = TcinfoTributacao(tribMun, tribFed, totTrib)
                     tribMun = TctribMunicipal(tribISSQN, cPaisResult, BM, exigSusp,
                                               tpImunidade, pAliq, tpRetISSQN)
                     tribFed = TctribNacional(piscofins, vRetCP, vRetIRRF, vRetCSLL)
                     totTrib = TctribTotal(vTotTrib, pTotTrib, indTotTrib, pTotTribSN)
```

## Montagem (padrão usado no motor)
- `Dps(versao="1.00", infDPS=inf)`; `inf.Id` = `"DPS" + <chave 43 dígitos>`.
  ⚠️ a chave real segue layout do padrão nacional — validar em homologação.
- Serializar: `XmlSerializer(SerializerConfig(pretty_print=True)).render(dps)` → XML
  `ns0:DPS xmlns:ns0="http://www.sped.fazenda.gov.br/nfse"`.
- Validar: round-trip com `lxml.etree.fromstring(xml)`. (nfelib não embala XSDs; não há
  validação de schema offline — validar contra a Fazenda em homologação.)

## DPS de exemplo (perfil ID — Simples Nacional, Aracaju 2800308)

```xml
<ns0:DPS xmlns:ns0="http://www.sped.fazenda.gov.br/nfse" versao="1.00">
  <ns0:infDPS Id="DPS…">
    <ns0:tpAmb>2</ns0:tpAmb>
    <ns0:dhEmi>2026-08-18T18:29:27-0300</ns0:dhEmi>
    <ns0:verAplic>1.0.0</ns0:verAplic>
    <ns0:serie>00001</ns0:serie><ns0:nDPS>0001</ns0:nDPS>
    <ns0:dCompet>2026-08-18</ns0:dCompet>
    <ns0:tpEmit>1</ns0:tpEmit>
    <ns0:cLocEmi>2800308</ns0:cLocEmi>
    <ns0:prest><ns0:CNPJ>54569818000159</ns0:CNPJ><ns0:IM>…</ns0:IM>
      <ns0:regTrib><ns0:opSimpNac>2</ns0:opSimpNac><ns0:regEspTrib>0</ns0:regEspTrib></ns0:regTrib>
    </ns0:prest>
    <ns0:toma>…</ns0:toma>
    <ns0:serv><ns0:locPrest><ns0:cLocPrestacao>2800308</ns0:cLocPrestacao></ns0:locPrest>
      <ns0:cServ><ns0:cTribNac>…</ns0:cTribNac><ns0:xDescServ>…</ns0:xDescServ><ns0:cNBS>…</ns0:cNBS></ns0:cServ>
    </ns0:serv>
    <ns0:valores><ns0:vServPrest><ns0:vServ>4850.00</ns0:vServ></ns0:vServPrest>
      <ns0:trib><ns0:tribMun><ns0:tribISSQN>1</ns0:tribISSQN><ns0:tpRetISSQN>1</ns0:tpRetISSQN></ns0:tribMun>
        <ns0:totTrib><ns0:indTotTrib>0</ns0:indTotTrib></ns0:totTrib>
      </ns0:trib>
    </ns0:valores>
  </ns0:infDPS>
</ns0:DPS>
```

## Assinatura/transmissão (Fase 2 — ainda não implementada)
- Assinar o `infDPS` com o A1: `erpbrasil.assinatura`.
- Transmitir ao ambiente nacional: `pynfse-nacional` (webservice do padrão nacional).
- Ambas exigem o certificado A1 real (pendência: `.pfx` num PC do principal).
