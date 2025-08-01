import React, { cache } from "react";
import { notFound } from "next/navigation";
import { ProductDetailThemeSelector } from "@/components/theme/ProductDetailThemeSelector";
import type { Metadata } from "next";
import { createBaseMetadata, getDynamicTitle } from "@/shared/utils/metadata";
import { fetchServiceById } from "@/services/marketplaceService";
import type { ServiceData } from "@/shared/types/marketplace";
import { Footer } from "@/shared/components/Footer";
import { Navigation } from "@/shared/components/Navigation";

interface ProductPageProps {
  params: Promise<{ id: string }>;
}

const getProductById = cache(
  async (id: string): Promise<ServiceData | null> => {
    try {
      const product = await fetchServiceById(id);
      return product;
    } catch (error) {
      console.error(`Error fetching product ${id}:`, error);
      return null;
    }
  }
);

// Generate metadata for SEO
export async function generateMetadata({
  params,
}: ProductPageProps): Promise<Metadata> {
  const { id } = await params;

  // use cached function to get data to generate metadata
  const product = await getProductById(id);

  if (product) {
    const title = await getDynamicTitle(product.name);
    return {
      ...createBaseMetadata(title),
      description:
        product.short_description ||
        `Discover ${product.name} and its powerful tools`,
    };
  }

  // default metadata if product not found
  const defaultTitle = await getDynamicTitle("Marketplace");
  return createBaseMetadata(defaultTitle);
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params;

  // use cached function to get product data (avoid duplicate API calls)
  const serviceData = await getProductById(id);

  if (!serviceData) {
    notFound();
  }

  return <ProductDetailThemeSelector product={serviceData} />;
}
