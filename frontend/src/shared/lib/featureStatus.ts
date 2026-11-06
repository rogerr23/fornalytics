/** Feature status from the product base, in plain words (shared by "Isso faz?" and Ideia × Código). */

export type FeatureStatus = 'implemented' | 'partial' | 'documented_only' | 'undocumented'

export const FEATURE_STATUS_TEXT: Record<FeatureStatus, string> = {
  implemented: 'implementada no código',
  partial: 'implementada em parte',
  documented_only: 'prometida no escopo e não encontrada no código',
  undocumented: 'existe no código, mas não estava no documento da ideia',
}
